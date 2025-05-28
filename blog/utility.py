        
# 清理空行和每行结尾的空白
import re


@staticmethod
def clean_up_text(text):
    # 移除 <br> 標籤
    text = re.sub(r'<br\s*/?>', '', text)
    # 清除连续的空行
    text = re.sub(r'\n\s*\n', '\n', text)
    # 移除开头和结尾的空白
    text = text.strip()
    # 移除每行结尾多余的空白
    text = "\n".join([line.strip() for line in text.splitlines()])
    return text

# 替换 URL 的函数，urls 改为 url_list
@staticmethod
def replace_specific_string_in_StringlistContent_with_custom_text(fullcontent, string_list, replacement=''):
    # 替换每个 URL 为自定义字符
    for str1 in string_list:
        fullcontent = fullcontent.replace(str1, replacement)  # 将每个 URL 替换为自定义字符
    return fullcontent