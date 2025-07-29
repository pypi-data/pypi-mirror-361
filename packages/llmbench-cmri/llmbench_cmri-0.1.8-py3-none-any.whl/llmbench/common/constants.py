from pathlib import Path

COMMON_MODEL_PATH = Path.home() / ".cache" / "huggingface" / "hub"
TOKENIZER_MODEL_PATH = COMMON_MODEL_PATH / "models--hf-internal-testing--llama-tokenizer"


class TOKENIZER_MODEL:
    """# 0: openai tiktoken 1: models--hf-internal-testing--llama-tokenizer"""
    tiktoken = 0
    llama = 1


default_tokenizer_model = TOKENIZER_MODEL.tiktoken


class METRICS:
    START_TIME = "start_time"  # 开始时间
    END_TIME = "end_time"  # 结束时间
    START_TIME_M = "start_time_m"  # 表示某个操作或任务的开始时间
    END_TIME_M = "end_time_m"  # 表示某个操作或任务的结束时间
    INTER_TOKEN_LAT = "inter_token_latency_s"  # 跨令牌延迟是指从一个令牌的开始处理到下一个令牌开始处理的时间间隔。它通常用于评估模型在生成文本或其他序列数据时的速度和效率。
    TTFT = "ttft_s"  # 是指从输入到输出第一个token的延迟时间
    E2E_LAT = "end_to_end_latency_s"  # 端到端延时（End-to-End Latency）是指数据在网络中从源头到目的地传输所需的总时间。
    NUM_INPUT_TOKENS = "number_input_tokens"  # 输入token数
    NUM_OUTPUT_TOKENS = "number_output_tokens"  # 输出token数
    NUM_TOTAL_TOKENS = "number_total_tokens"   # 总token数
    REQ_OUTPUT_THROUGHPUT = "request_output_throughput_token_per_s"  # 请求输出吞吐量，以每秒token数表示
    ERROR_MSG = "error_msg"  # 错误消息
    ERROR_CODE = "error_code"  # 错误代码
    ERROR_CODE_FREQ = "error_code_frequency"  # 错误代码频率
    NUM_ERRORS = "number_errors"  # 错误数量
    OUTPUT_THROUGHPUT = "mean_output_throughput_token_per_s"  # 平均输出吞吐量，以每秒token数表示
    NUM_COMPLETED_REQUESTS = "num_completed_requests"  # 已完成的请求数量
    COMPLETED_REQUESTS_PER_MIN = "num_completed_requests_per_min"  # 每分钟完成的请求数量
    ERROR_RATE = "error_rate"  # 错误率
    NUM_REQ_STARTED = "num_requests_started"  # 已启动的请求数量
    TOTAL_COST_TIME = "total_cost_time_s"  # 总成本时间
    REQUEST_CONTENT = "request_content"  # 请求内容
    RESPONSE_CONTENT = "response_content"  # 响应内容
    EXTRA_DATA = "extra_data"  # 额外数据
