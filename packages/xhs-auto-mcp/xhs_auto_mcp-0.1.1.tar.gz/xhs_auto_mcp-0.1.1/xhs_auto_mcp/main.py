import sys
from typing import Annotated, Any, List, Dict, Optional
import asyncio
import concurrent
import tempfile
import time
import json
import os
from datetime import datetime
from fastmcp import FastMCP
from dotenv import load_dotenv

from pydantic import Field
import requests
from xhs_auto_mcp.tools.write_xiaohongshu import XiaohongshuPoster
from mcp.types import TextContent
from xhs_auto_mcp.tools.xhs_api import XhsApi
from xhs_auto_mcp.tools.log_utils import logger, setup_logger
from urllib.parse import urlparse, parse_qs
import argparse

# 配置日志
setup_logger(log_level="INFO")

parser = argparse.ArgumentParser()

parser.add_argument("--transport", type=str, default='http')
parser.add_argument("--port", type=int, default=8809)
parser.add_argument("--host", type=str, default='0.0.0.0')

args = parser.parse_args()

mcp = FastMCP("小红书内容获取及自动发布", port=args.port)

# 加载.env文件中的环境变量
load_dotenv()

xhs_cookie = os.getenv('XHS_COOKIE')
# 默认缓存路径为当前目录
path= os.getenv("JSON_PATH","./")
slow_mode=os.getenv("SLOW_MODE","False").lower() == "true"

xhs_api = XhsApi(cookie=xhs_cookie)


def get_nodeid_token(url=None, note_ids=None):
    if note_ids is not None:
        note_id = note_ids[0,24]
        xsec_token = note_ids[24:]
        return {"note_id": note_id, "xsec_token": xsec_token}
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    note_id = parsed_url.path.split('/')[-1]
    xsec_token = None
    xsec_token_list = query_params.get('xsec_token', [None])
    if len(xsec_token_list) > 0:
        xsec_token = xsec_token_list[0]
    return {"note_id": note_id, "xsec_token": xsec_token}

def download_image(url):
    local_filename = url.split('/')[-1]
    temp_dir = tempfile.gettempdir()

    local_path = os.path.join(temp_dir, local_filename)  # 假设缓存地址为/tmp
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_path

def download_images_parallel(urls):
    """
    并行下载图片到本地缓存地址
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(download_image, urls))
    return results


@mcp.tool()
async def check_content_cookie() -> str:
    """
    小红书内容平台工具
    检测小红书内容平台cookie是否有效
    
    Returns:
        str: "cookie有效" 或 "cookie已失效"
    """
    try:
        data = await xhs_api.get_me()

        if 'success' in data and data['success'] == True:
            return "cookie有效"
        else:
            return "cookie已失效"
    except Exception as e:
        logger.error(e)
        return "cookie已失效"


@mcp.tool()
async def home_feed() -> str:
    """
    小红书内容平台工具
    获取首页推荐笔记
    
    Returns:
        str: 首页推荐笔记列表
    """
    data = await xhs_api.home_feed()
    result = "搜索结果：\n\n"
    if 'data' in data and 'items' in data['data'] and len(data['data']['items']) > 0:
        for i in range(0, len(data['data']['items'])):
            item = data['data']['items'][i]
            if 'note_card' in item and 'display_title' in item['note_card']:
                title = item['note_card']['display_title']
                liked_count = item['note_card']['interact_info']['liked_count']
                # cover=item['note_card']['cover']['url_default']
                url = f'https://www.xiaohongshu.com/explore/{item["id"]}?xsec_token={item["xsec_token"]}'
                result += f"{i}. {title}  \n 点赞数:{liked_count} \n   链接: {url}  \n\n"
    else:
        result = await check_content_cookie()
        if "有效" in result:
            result = f"未找到相关的笔记"
    return result

@mcp.tool()
async def search_notes(keywords: Annotated[str, Field(description="搜索关键词")]) -> str:
    """
    小红书内容平台工具
    根据关键词搜索笔记
    
    Returns:
        str: 搜索结果
    """

    data = await xhs_api.search_notes(keywords)
    logger.info(f'keywords:{keywords},data:{data}')
    result = "搜索结果：\n\n"
    if 'data' in data and 'items' in data['data'] and len(data['data']['items']) > 0:
        for i in range(0, len(data['data']['items'])):
            item = data['data']['items'][i]
            if 'note_card' in item and 'display_title' in item['note_card']:
                title = item['note_card']['display_title']
                liked_count = item['note_card']['interact_info']['liked_count']
                # cover=item['note_card']['cover']['url_default']
                url = f'https://www.xiaohongshu.com/explore/{item["id"]}?xsec_token={item["xsec_token"]}'
                result += f"{i}. {title}  \n 点赞数:{liked_count} \n   链接: {url}  \n\n"
    else:
        result = await check_content_cookie()
        if "有效" in result:
            result = f"未找到与\"{keywords}\"相关的笔记"
    return result


@mcp.tool()
async def get_note_content(url: Annotated[str, Field(description="笔记url,要带上xsec_token")]) -> str:
    """
    小红书内容平台工具
    获取笔记详细内容
    
    Returns:
        str: 笔记内容
    """
    params = get_nodeid_token(url=url)
    data = await xhs_api.get_note_content(**params)
    logger.info(f'url:{url},data:{data}')
    result = ""
    if 'data' in data and 'items' in data['data'] and len(data['data']['items']) > 0:
        for i in range(0, len(data['data']['items'])):
            item = data['data']['items'][i]

            if 'note_card' in item and 'user' in item['note_card']:
                note_card = item['note_card']
                cover = ''
                if 'image_list' in note_card and len(note_card['image_list']) > 0 and note_card['image_list'][0][
                    'url_pre']:
                    cover = note_card['image_list'][0]['url_pre']

                data_format = datetime.fromtimestamp(note_card.get('time', 0) / 1000)
                liked_count = item['note_card']['interact_info']['liked_count']
                comment_count = item['note_card']['interact_info']['comment_count']
                collected_count = item['note_card']['interact_info']['collected_count']

                url = f'https://www.xiaohongshu.com/explore/{params["note_id"]}?xsec_token={params["xsec_token"]}'
                result = f"标题: {note_card.get('title', '')}\n"
                result += f"作者: {note_card['user'].get('nickname', '')}\n"
                result += f"发布时间: {data_format}\n"
                result += f"点赞数: {liked_count}\n"
                result += f"评论数: {comment_count}\n"
                result += f"收藏数: {collected_count}\n"
                result += f"链接: {url}\n\n"
                result += f"内容:\n{note_card.get('desc', '')}\n"
                result += f"封面:\n{cover}"

            break
    else:
        result = await check_content_cookie()
        if "有效" in result:
            result = "获取失败"
    return result


@mcp.tool()
async def get_note_comments(url: Annotated[str, Field(description="笔记url,要带上xsec_token")]) -> str:
    """
    小红书内容平台工具
    获取笔记评论
    
    Returns:
        str: 笔记评论
    """
    params = get_nodeid_token(url=url)

    data = await xhs_api.get_note_comments(**params)
    logger.info(f'url:{url},data:{data}')

    result = ""
    if 'data' in data and 'comments' in data['data'] and len(data['data']['comments']) > 0:
        for i in range(0, len(data['data']['comments'])):
            item = data['data']['comments'][i]
            data_format = datetime.fromtimestamp(item['create_time'] / 1000)

            result += f"{i}. {item['user_info']['nickname']}（{data_format}）: {item['content']}\n\n"

    else:
        result = await check_content_cookie()
        if "有效" in result:
            result = "暂无评论"

    return result


@mcp.tool()
async def post_comment(comment: Annotated[str, Field(description="评论内容")], note_id: Annotated[str, Field(description="笔记id")]) -> str:
    """
    小红书内容平台工具
    进行评论到指定笔记
    
    Returns:
        str: 发布结果
    """
    # params = get_nodeid_token(url)
    response = await xhs_api.post_comment(note_id, comment)
    if 'success' in response and response['success'] == True:
        return "回复成功"
    else:
        # 直接实现cookie检查逻辑，而不是调用check_content_cookie工具
        try:
            data = await xhs_api.get_me()
            if 'success' in data and data['success'] == True:
                return "回复失败"
            else:
                return "cookie已失效"
        except Exception as e:
            logger.error(e)
            return "cookie已失效"
        
@mcp.tool()
def login(phone: Annotated[str, Field(description="手机号")], country_code: Annotated[Optional[str], Field(description="国家代码")] = "+86"):
    """
    小红书创作平台工具
    打开浏览器，发送验证码，等待用户输入验证码，登录小红书创作平台
    若用户未提供手机号，请告诉用户，请提供手机号

    Returns:
        str: 打开浏览器及发送验证码结果
    """
    # 重置之前可能存在的实例
    XiaohongshuPoster.reset_instance()
    
    # 创建新实例
    poster = XiaohongshuPoster(path)
    success, message = poster.login(phone, country_code)
    
    # 不关闭浏览器，让它保持打开状态等待验证码
    return message

@mcp.tool()
def wait_for_verify_code(verification_code: Annotated[str, Field(description="验证码")]):
    """
    小红书创作平台工具
    等待用户输入验证码，登录小红书创作平台
    
    Returns:
        str: 验证码输入结果，及登录结果
    """
    # 使用已存在的实例
    poster = XiaohongshuPoster(path)
    success, message = poster.wait_for_verify_code(verification_code)
    return message

@mcp.tool()
def create_note_with_images(title: Annotated[str, Field(description="小红书笔记标题，不能超过20个字")], content: Annotated[str, Field(description="小红书笔记正文内容，不能超过1000个字")], image_paths: Annotated[Optional[str], Field(description="本地图片路径,多个路径用逗号分隔")] = None, image_urls: Annotated[Optional[str], Field(description="图片URL链接,多个URL用逗号分隔")] = None) -> list[TextContent]:
    """
    小红书创作平台工具
    创建小红书笔记支持本地图片和图片URL,必须提供图片路径或URL。
    如果提供图片URL,则忽略本地图片路径,如果提供本地图片路径则忽略图片URL,如果都提供，则优先使用本地图片路径
    
    Returns:
        list[TextContent]: 发布结果
    """
    poster = XiaohongshuPoster(path)
    #poster.login(phone)
    res = ""
    try:
        images = []
        
        # 处理本地图片路径
        if image_paths:
            local_paths = [path.strip() for path in image_paths.split(',')]
            # 检查图片文件是否存在
            for img_path in local_paths:
                if not os.path.exists(img_path):
                    logger.error(f"图片文件不存在: {img_path}")
                    return [TextContent(type="text", text=f"错误：图片文件不存在: {img_path}")]
                else:
                    logger.info(f"图片文件存在: {img_path}")
            images.extend(local_paths)
            
        # 处理图片URL
        if not images and image_urls:
            urls = [url.strip() for url in image_urls.split(',')]
            if urls:
                # 使用并行下载图片
                try:
                    downloaded_images = download_images_parallel(urls)
                    images.extend(downloaded_images)
                    logger.info(f"成功下载图片: {downloaded_images}")
                except Exception as e:
                    logger.error(f"下载图片失败: {str(e)}")
                    return [TextContent(type="text", text=f"错误：下载图片失败: {str(e)}")]
                
        # 确保至少有一张图片
        if not images:
            return [TextContent(type="text", text="错误：至少需要提供一张图片（本地路径或URL）")]
            
        logger.info(f"准备发布笔记，标题: {title}, 内容长度: {len(content)}, 图片数量: {len(images)}")
        code, info = poster.login_to_publish(title, content, images, slow_mode)
        logger.info(f"发布结果: 成功={code}, 信息={info}")
        res = info
    except Exception as e:
        logger.error(f"发布笔记异常: {str(e)}", exc_info=True)
        res = f"error: {str(e)}"
    finally:
        try:
            poster.close()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器时发生错误: {str(e)}")

    return [TextContent(type="text", text=res)]

@mcp.tool()
def create_note_with_videos(title: Annotated[str, Field(description="小红书笔记标题，不能超过20个字")], content: Annotated[str, Field(description="小红书笔记正文内容，不能超过1000个字")], video_paths: Annotated[Optional[str], Field(description="本地视频路径,多个路径用逗号分隔")] = None, video_urls: Annotated[Optional[str], Field(description="视频URL链接,多个URL用逗号分隔")] = None) -> list[TextContent]:
    """
    小红书创作平台工具
    创建小红书笔记支持本地视频和视频URL,必须提供视频路径或URL 。
    如果提供视频URL,则忽略本地视频路径,如果提供本地视频路径则忽略视频URL,如果都提供，则优先使用本地视频路径
    
    Returns:
        list[TextContent]: 发布结果
    """
    poster = XiaohongshuPoster(path)
    #poster.login(phone)
    res = ""
    try:
        videos = []
        
        # 处理本地视频路径
        if video_paths:
            local_paths = [path.strip() for path in video_paths.split(',')]
            # 检查视频文件是否存在
            for video_path in local_paths:
                if not os.path.exists(video_path):
                    logger.error(f"视频文件不存在: {video_path}")
                    return [TextContent(type="text", text=f"错误：视频文件不存在: {video_path}")]
                else:
                    logger.info(f"视频文件存在: {video_path}")
            videos.extend(local_paths)
            
        # 处理视频URL
        if not videos and video_urls:
            urls = [url.strip() for url in video_urls.split(',')]
            if urls:
                # 使用并行下载视频
                try:
                    downloaded_videos = download_images_parallel(urls)
                    videos.extend(downloaded_videos)
                    logger.info(f"成功下载视频: {downloaded_videos}")
                except Exception as e:
                    logger.error(f"下载视频失败: {str(e)}")
                    return [TextContent(type="text", text=f"错误：下载视频失败: {str(e)}")]
                
        # 确保至少有一个视频
        if not videos:
            return [TextContent(type="text", text="错误：至少需要提供一个视频（本地路径或URL）")]
            
        logger.info(f"准备发布视频笔记，标题: {title}, 内容长度: {len(content)}, 视频数量: {len(videos)}")
        code, info = poster.login_to_publish_video(title, content, videos, slow_mode)
        logger.info(f"发布结果: 成功={code}, 信息={info}")
        res = info
    except Exception as e:
        logger.error(f"发布视频笔记异常: {str(e)}", exc_info=True)
        res = f"error: {str(e)}"
    finally:
        try:
            poster.close()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器时发生错误: {str(e)}")

    return [TextContent(type="text", text=res)]

def app():
    host = args.host
    port = args.port
    transport = args.transport
    try:
        if transport == "http":
            mcp.run(host=host, port=port, transport=transport)
        elif transport == "stdio":
            mcp.run(transport=transport)
        else:
            raise ValueError("不支持的端口形式")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    app()