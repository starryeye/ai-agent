"""데이터 분석 MCP 서버.

CSV 통계 요약 / 히스토그램 / 자동 모델 학습 도구를 MCP 도구로 노출한다.
stdio 트랜스포트로 실행되며, data_client.py 가 이 서버에 붙어 도구를 사용한다.

MCP(Model Context Protocol): LLM 에이전트가 외부 "도구 서버"를 표준 프로토콜로
연결해 쓰는 방식. 도구 구현(서버)과 사용(클라이언트)을 분리할 수 있다.
"""
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, root_mean_squared_error
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# MCP 서버 인스턴스 (이름은 클라이언트에서 식별용)
mcp = FastMCP("DataAnalysis")


@mcp.tool()
def describe_column(csv_path: str, column: str) -> dict:
    """CSV 특정 컬럼의 요약 통계(count/mean/std/min/max 등)를 반환한다.

    Args:
        csv_path (str): CSV 파일 경로
        column (str): 통계를 낼 컬럼명
    """
    df = pd.read_csv(csv_path)
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in CSV.")
    return df[column].describe().to_dict()


@mcp.tool()
def plot_histogram(csv_path: str, column: str, bins: int = 10) -> str:
    """CSV 특정 컬럼의 밀도 히스토그램을 그려 이미지로 저장하고 경로를 반환한다.

    Args:
        csv_path (str): CSV 파일 경로
        column (str): 시각화할 컬럼명
        bins (int): 히스토그램 구간 수 (기본 10)
    """
    df = pd.read_csv(csv_path)
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in CSV.")

    plt.figure(figsize=(8, 6))
    sns.histplot(
        df[column].dropna(), bins=bins, kde=True,
        stat="density", edgecolor="black", alpha=0.6,
    )
    plt.xlabel(column)
    plt.ylabel("Density")
    plt.title(f"Density Histogram of {column}")

    output_path = f"{column}_density_hist.png"
    plt.savefig(output_path)
    plt.close()
    return output_path


@mcp.tool()
def model(csv_path: str, x_columns: list, y_column: str) -> dict:
    """타깃 컬럼 타입에 따라 분류/회귀 모델을 자동 학습하고 성능을 반환한다.

    Args:
        csv_path: CSV 파일 경로
        x_columns: 피처 컬럼명 리스트
        y_column: 타깃 컬럼명
    """
    df = pd.read_csv(csv_path)
    for col in x_columns + [y_column]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in CSV.")

    X = df[x_columns].copy()
    y = df[y_column]

    # 범주형 피처는 라벨 인코딩
    for col in X.select_dtypes(include=["object"]).columns:
        X[col] = LabelEncoder().fit_transform(X[col])

    # 타깃이 문자열이거나 고유값 10개 이하면 분류로 판단
    is_classification = y.dtype == "object" or len(y.unique()) <= 10

    if is_classification:
        y = LabelEncoder().fit_transform(y)
        clf = RandomForestClassifier()
        metric_name = "accuracy"
    else:
        clf = RandomForestRegressor()
        metric_name = "rmse"

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    if is_classification:
        score = accuracy_score(y_test, y_pred)
        model_type = "classification"
    else:
        score = root_mean_squared_error(y_test, y_pred)
        model_type = "regression"

    return {"model_type": model_type, "metric": metric_name, "score": float(score)}


@mcp.prompt()
def default_prompt(message: str) -> list[base.Message]:
    """클라이언트가 불러다 쓰는 기본 시스템 프롬프트 + 사용자 메시지."""
    return [
        base.AssistantMessage(
            "You are a helpful data analysis assistant.\n"
            "Please clearly organize and return the tool calling results and the data analysis."
        ),
        base.UserMessage(message),
    ]


if __name__ == "__main__":
    # stdio 트랜스포트: 클라이언트가 이 스크립트를 subprocess 로 띄워 표준입출력으로 통신
    mcp.run(transport="stdio")
