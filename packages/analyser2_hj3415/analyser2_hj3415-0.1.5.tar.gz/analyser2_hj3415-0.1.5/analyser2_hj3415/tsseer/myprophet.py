from prophet import Prophet
import pandas as pd
import os, json, redis
from sklearn.preprocessing import StandardScaler

from analyser2_hj3415.tsseer.utils import get_raw_data
from analyser2_hj3415.common.connection import get_redis_client

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


def prepare_prophet_data(df: pd.DataFrame) -> dict[str, pd.DataFrame | StandardScaler]:
    # ── (1) 기본 정리 ────────────────────────────────────
    df.columns = df.columns.get_level_values(0)
    df.index   = df.index.tz_localize(None)
    df = df[['Close', 'Volume']].dropna().reset_index()
    df.columns = ['ds', 'y', 'volume']          # Prophet 규격

    # ── (2) 스케일러 두 개 생성 ─────────────────────────
    volume_scaler = StandardScaler()
    y_scaler      = StandardScaler()

    df['volume_scaled'] = volume_scaler.fit_transform(df[['volume']])
    df['y_scaled']      = y_scaler.fit_transform(df[['y']])

    return {
        'prepared_df'   : df,              # y/raw, y_scaled, volume_scaled 모두 보존
        'volume_scaler' : volume_scaler,
        'y_scaler'      : y_scaler,
    }


def run_prophet_forecast(df_scaler_dict: dict[str, object], periods: int = 180) -> pd.DataFrame:
    """Prophet 학습 & periods 일 예측 → 역-스케일링해서 반환"""

    # ── 0. 필요한 객체 꺼내기 ───────────────────────────
    df:            pd.DataFrame   = df_scaler_dict['prepared_df'].copy()
    vol_scaler:    StandardScaler = df_scaler_dict['volume_scaler']
    y_scaler:      StandardScaler = df_scaler_dict['y_scaler']

    # ── 1. Prophet 학습용 DF 생성 (y_scaled만 사용) ────
    prophet_df = (
        df[['ds', 'y_scaled', 'volume_scaled']]
        .rename(columns={'y_scaled': 'y'})
    )

    model = Prophet()
    model.add_regressor('volume_scaled')
    model.fit(prophet_df)

    # ── 2. 미래 데이터프레임 생성 ───────────────────────
    future = model.make_future_dataframe(periods=periods)

    mean_vol = df['volume'].mean()
    future['volume_scaled'] = vol_scaler.transform([[mean_vol]] * len(future))

    # ── 3. 예측 + y 역-스케일링 ─────────────────────────
    pred_df = model.predict(future)

    cols_to_inverse = ['yhat', 'yhat_lower', 'yhat_upper']
    pred_df[cols_to_inverse] = y_scaler.inverse_transform(pred_df[cols_to_inverse])

    # (선택) 학습 구간의 실측 y도 복원해 두면 병합/시각화에 편리
    df['y'] = y_scaler.inverse_transform(df[['y_scaled']])
    # pred_df 와 df 를 나중에 merge 하면 실측·예측을 한 눈에 볼 수 있음

    return pred_df

# ── redis 연결──────────────────────

# ── 캐싱 버전 serve_myprophet_forecast ────────────────────────────
def cached_prophet_forecast(ticker: str, periods: int = 180) -> dict[str, list]:
    """
    1) redis 에 prophet:{ticker} 키가 있으면 그대로 반환
    2) 없으면 예측 계산 → 캐시에 저장(setex) → 반환
    """
    redis_cli = get_redis_client()
    ttl = int(os.getenv('REDIS_EXPIRE_TIME_H', 12)) * 60 * 60

    cache_key = f"prophet:{ticker.lower()}"

    # 1. 캐시 조회 ---------------------------------------------------
    try:
        if (raw := redis_cli.get(cache_key)):
            mylogger.info(f"cache hit {cache_key}")
            return json.loads(raw)
    except redis.RedisError as e:
        mylogger.warning(f"Redis GET fail: {e}")

    # 2. 캐시 미스 → 예측 계산 --------------------------------------
    mylogger.info(f"Prophet cache miss: {cache_key} — start forecasting")

    # 2-1 데이터 준비
    df = get_raw_data(ticker)
    df_scaler_dict = prepare_prophet_data(df)

    # 2-2 예측
    past_and_forecast_df = run_prophet_forecast(df_scaler_dict, periods)

    # 2-3 직렬화용 머지
    prepared_df: pd.DataFrame = df_scaler_dict['prepared_df']
    merged = (
        prepared_df[['ds', 'y']]
        .merge(
            past_and_forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
            on='ds', how='outer'
        )
        .sort_values('ds')
    )

    result: dict[str, list] = {
        'ds'      : merged['ds'].dt.strftime('%Y-%m-%d').tolist(),
        'actual'  : merged['y'].where(merged['y'].notna()).tolist(),
        'forecast': merged['yhat'].round(2).tolist(),
        'lower'   : merged['yhat_lower'].round(2).tolist(),
        'upper'   : merged['yhat_upper'].round(2).tolist(),
    }

    # 3. 캐시에 저장 -------------------------------------------------
    try:
        redis_cli.setex(cache_key, ttl, json.dumps(result))
        mylogger.info(f"cache save {cache_key} (ttl={ttl})")
    except redis.RedisError as e:
        mylogger.warning(f"Redis SETEX fail: {e}")

    return result



