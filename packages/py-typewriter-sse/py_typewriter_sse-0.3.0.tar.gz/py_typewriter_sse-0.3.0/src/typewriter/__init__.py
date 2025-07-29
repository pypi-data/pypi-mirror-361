# src/typewriter/__init__.py

import random
import string
import sys
import time
from collections.abc import Generator
from typing import Tuple

try:
    import jieba
except ImportError:
    jieba = None

__all__ = ["typewrite", "generate_typewriter_flow"]
__version__ = "0.3.0"


PUNCTUATION_EXTENDED = set(string.punctuation) | {
    " ",
    "　",  # 空格和全角空格
    "，",
    "。",
    "！",
    "？",
    "…",
    "；",
    "：",
    "“",
    "”",
    "‘",
    "’",
    "（",
    "）",
    "《",
    "》",
    "【",
    "】",
    "、",
}

END_PUNCTUATION = ".。", "!", "！", "?", "？", "…"


def generate_typewriter_flow(
    text: str, base_delay: float = 0.05, mode: str = "char", max_chunk_size=15, min_chunk_size=5
) -> Generator[Tuple[str, float], None, None]:
    """
    生成一个模拟打字机效果的字符或词语流。

    它会 yield 一个元组，包含 (下一个文本片段, 延迟时间)。

    :param text: 要处理的文本。
    :param base_delay: 基础延迟时间（秒）。一个字符的平均延迟时间。
    :param mode: 切分模式。
                 'char' (默认): 按单个字符切分，适用于所有语言。
                 'word': 使用 jieba 按词语切分，对中文效果更佳。

    :return:  (文本片段, 延迟时间) 的生成器。

    用法:
        # 模式一：字符模式 (默认)
        flow_char = generate_typewriter_flow("Hello, world! 你好，世界！")
        for char, delay in flow_char:
            print(char, end='', flush=True)
            time.sleep(delay)
        print('\\n---')

        # 模式二：中文分词模式
        flow_word = generate_typewriter_flow("Jieba是一个强大的中文分词库。", mode='word')
        for word, delay in flow_word:
            print(word, end='', flush=True)
            time.sleep(delay)
    """
    if mode == "word":
        if jieba is None:
            raise ImportError("Jieba library is not installed. Please run 'pip install jieba' to use 'word' mode.")
        token_generator = jieba.cut(text)
    else:
        token_generator = iter(text)

    chunk_buffer = []  # 用于存储 token 的缓冲区

    for token in token_generator:
        chunk_buffer.append(token)

        # 检查是否满足“吐出”条件
        # 条件1：当前 token 是一个显著的标点，并且块已达到最小尺寸
        # 这样做是为了避免像 "Dr." 这样的情况被过早切分
        is_punctuation_break = token in END_PUNCTUATION and len(chunk_buffer) >= min_chunk_size

        # 条件2：块的长度达到了最大值
        is_max_size_reached = len(chunk_buffer) >= max_chunk_size

        if is_punctuation_break or is_max_size_reached:
            # 将缓冲区中的 token 合并成一个字符串
            chunk_to_yield = "".join(chunk_buffer)

            # --- 延迟计算逻辑 ---
            # 延迟时间主要由块的最后一个 token 决定
            last_token = chunk_buffer[-1]
            delay = 0

            if last_token in END_PUNCTUATION:
                # 对于句末标点，给予较长的停顿
                delay = base_delay * 8  # 句末停顿可以更长一些
            elif last_token in PUNCTUATION_EXTENDED:
                # 对于普通标点，如逗号，给予中等停顿
                delay = base_delay * 3
            else:
                # 如果块是因为达到最大长度而结束，给予一个标准短停顿
                delay = base_delay

            # 确保延迟不会过小
            delay = max(0.02, delay)

            yield chunk_to_yield, delay

            # 清空缓冲区，为下一个块做准备
            chunk_buffer = []

    # 循环结束后，如果缓冲区中还有剩余的 token，将它们作为最后一个块吐出
    if chunk_buffer:
        chunk_to_yield = "".join(chunk_buffer)
        # 最后的块通常没有特定停顿，给一个基础延迟即可
        yield chunk_to_yield, base_delay


def typewrite(text: str, delay: float = 0.05, end: str = "\n") -> None:
    """
    以打字机效果直接在终端打印文本。

    这是一个高级、易于使用的函数，封装了生成和打印的整个过程。

    :param text: 要打印的文本。
    :param delay: 每个字符之间的平均延迟时间（秒）。
    :param end: 文本打印完毕后追加的字符，默认为换行符。

    用法:
        >>> typewrite("你好，世界！")
    """
    flow_generator = generate_typewriter_flow(text, base_delay=delay)

    for char, sleep_time in flow_generator:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(sleep_time)

    sys.stdout.write(end)
    sys.stdout.flush()


if __name__ == "__main__":
    text_sample_cn = "你好，世界！这是一个基于Jieba分词的打字机效果模拟。它能让中文输出更自然、流畅。"
    text_sample_en = "Hello, world! This is a typewriter effect simulation."

    print("--- 模式: 'char' (默认字符模式) ---")
    flow_char = generate_typewriter_flow(text_sample_cn, base_delay=0.03)
    for char, delay in flow_char:
        print(char, end="", flush=True)  # flush=True 确保立即输出
        time.sleep(delay)
    print("\n")  # 换行

    print("--- 模式: 'word' (Jieba分词模式) 快速（多词合并输出,适合长文本）---")
    try:
        flow_word = generate_typewriter_flow(text_sample_cn, base_delay=0.03, mode="word")
        for word, delay in flow_word:
            print(word, end="", flush=True)
            time.sleep(delay)
        print("\n")
    except ImportError as e:
        print(f"\n错误: {e}")

    print("--- 模式: 'word' (Jieba分词模式) 慢速（逐词输出）---")
    try:
        flow_word = generate_typewriter_flow(
            text_sample_cn, base_delay=0.03, mode="word", max_chunk_size=1, min_chunk_size=1
        )
        for word, delay in flow_word:
            print(word, end="", flush=True)
            time.sleep(delay)
        print("\n")
    except ImportError as e:
        print(f"\n错误: {e}")

    print("--- 英文文本在 'word' 模式下的效果 ---")
    # Jieba 也能很好地处理英文和数字
    try:
        flow_en_word = generate_typewriter_flow(text_sample_en, base_delay=0.03, mode="word")
        for word, delay in flow_en_word:
            print(word, end="", flush=True)
            time.sleep(delay)
        print("\n")
    except ImportError as e:
        print(f"\n错误: {e}")
