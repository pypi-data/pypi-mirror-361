本文介绍通义万相-通用图像编辑模型的输入输出参数。

该模型通过简单的指令即可实现多样化的图像编辑，适用于扩图、去水印、风格迁移、图像修复、图像美化等场景。 当前支持以下功能：

图像风格化：全局风格化、局部风格化。
图像内容编辑：指令编辑（无需指定区域，仅通过指令增加/修改图片内容）、局部重绘（针对指定区域增加/删除/修改图片内容）、去文字水印（中英文）。
图像尺寸与分辨率优化：扩图（按比例扩图）、图像超分（高清放大）。
图像色彩处理：图像上色（黑白或灰度图像转为彩色图像）。
基于参考图像生成：线稿生图（先提取输入图像的线稿，再参考线稿生成图像）、参考卡通形象生图。
相关指南：通用图像编辑

模型概览

模型名称
计费单价
限流（主账号与RAM子账号共用）
免费额度
任务下发接口RPS限制
同时处理中任务数量
wanx2.1-imageedit
0.14元/张
2
2
免费额度：500张
有效期：阿里云百炼开通后180天内
更多说明请参见模型计费与限流。

模型效果

模型功能
输入图像
输入提示词
输出图像
全局风格化
image
转换成法国绘本风格
image
局部风格化
image
把房子变成木板风格。
image
指令编辑
image
把女孩的头发修改为红色。
image
局部重绘
输入图像
image
输入涂抹区域图像（白色为涂抹区域）
image
一只陶瓷兔子抱着一朵陶瓷花。
输出图像
image
去文字水印
image
去除图像中的文字。
image
扩图
20250319105917
一位绿色仙子。
image
图像超分
模糊图像
image
图像超分。
清晰图像
image
图像上色
image
蓝色背景，黄色的叶子。
image
线稿生图
输入图像
image
北欧极简风格的客厅。
提取原图的线稿并生成图像
image
参考卡通形象生图
输入参考图（卡通形象）
image
卡通形象小心翼翼地探出头，窥视着房间内一颗璀璨的蓝色宝石。
输出图像
image
前提条件

通义万相-通用图像编辑API支持通过HTTP和DashScope SDK进行调用。

在调用前，您需要开通模型服务并获取API Key，再配置API Key到环境变量。

如需通过SDK进行调用，请安装DashScope SDK。目前，该SDK已支持Python和Java。

HTTP调用

图像模型处理时间较长，为了避免请求超时，HTTP调用仅支持异步获取模型结果。您需要发起两个请求：

创建任务获取任务ID：首先发起创建任务请求，该请求会返回任务ID（task_id）。
根据任务ID查询结果：使用上一步获得的任务ID，查询任务状态及结果。任务成功执行时将返回图像URL，有效期24小时。
说明
创建任务后，该任务将被加入到排队队列，等待调度执行。后续需要调用“根据任务ID查询结果接口”获取任务状态及结果。
通用图像编辑模型大约需要5-15秒。实际耗时取决于排队任务数量和网络状况，请您在获取结果时耐心等待。
步骤1：创建任务获取任务ID

POST https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis

请求参数

全局风格化局部风格化指令编辑局部重绘去文字水印扩图图像超分图像上色线稿生图参考卡通形象生图
 
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis' \
--header 'X-DashScope-Async: enable' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--header 'Content-Type: application/json' \
--data '{
  "model": "wanx2.1-imageedit",
  "input": {
    "function": "stylization_all",
    "prompt": "转换成法国绘本风格",
    "base_image_url": "http://wanx.alicdn.com/material/20250318/stylization_all_1.jpeg"
  },
  "parameters": {
    "n": 1
  }
}'
请求头（Headers）

Content-Type string （必选）
请求内容类型。此参数必须设置为application/json。
Authorization string（必选）
请求身份认证。接口使用阿里云百炼API-Key进行身份认证。示例值：Bearer d1xxx2a。
X-DashScope-Async string （必选）
异步处理配置参数。HTTP请求只支持异步，必须设置为enable。
请求体（Request Body）

model string （必选）
模型名称。示例值：wanx2.1-imageedit。
input object （必选）
输入的基本信息，如提示词等。
属性
prompt string （必选）
提示词，用来描述生成图像中期望包含的元素和视觉特点。
支持中英文，长度不超过800个字符，每个汉字/字母占一个字符，超过部分会自动截断。
不同功能的提示词存在差异，建议根据具体功能参考相应的技巧说明。
function string （必选）
图像编辑功能。目前支持的功能有：
stylization_all：全局风格化，当前支持2种风格。风格和提示词技巧
stylization_local：局部风格化，当前支持8种风格。风格和提示词技巧
description_edit：指令编辑。通过指令即可编辑图像，简单编辑任务优先推荐这种方式。提示词技巧
description_edit_with_mask：局部重绘。需要指定编辑区域，适合对编辑范围有精确控制的场景。提示词技巧
remove_watermark：去文字水印。提示词技巧
expand：扩图。提示词技巧
super_resolution：图像超分。提示词技巧
colorization：图像上色。提示词技巧
doodle：线稿生图。提示词技巧
control_cartoon_feature：参考卡通形象生图。提示词技巧
base_image_url string （必选）
输入图像的URL地址。
URL 需为公网可访问地址，支持 HTTP 或 HTTPS 协议。您也可在此获取临时公网URL。
图像限制：
图像格式：JPG、JPEG、PNG、BMP、TIFF、WEBP。
图像分辨率：图像的宽度和高度范围为[512, 4096]像素。
图像大小：不超过10MB。
URL地址中不能包含中文字符。
mask_image_url string （可选）
仅当function设置为description_edit_with_mask（局部重绘）时必填，其余情况无需填写。
URL 需为公网可访问地址，支持 HTTP 或 HTTPS 协议。您也可在此获取临时公网URL。
涂抹区域图像要求：
数据格式 ：仅支持图像URL地址，不支持Base64数据。
图像分辨率 ：必须与base_image_url的图像分辨率保持一致。图像宽度和高度需在[512, 4096]像素之间。
图像格式 ：支持JPG、JPEG、PNG、BMP、TIFF、WEBP。
图像大小 ：不超过10MB。
URL地址中不能包含中文字符。
涂抹区域颜色要求：
白色区域 ：表示需要编辑的部分，必须使用纯白色（RGB值为[255,255,255]），否则可能无法正确识别。
黑色区域：表示无需改变的部分，必须使用纯黑色（RGB值为[0,0,0]），否则可能无法正确识别。
关于如何获取涂抹区域图像：使用PS抠图或其他工具生成黑白涂抹图像。
parameters object （可选）
图像处理参数。
属性
通用全局风格化指令编辑扩图图像超分线稿生图
n integer （可选）
生成图片的数量。取值范围为1~4张，默认为1。
seed integer （可选）
随机数种子，用于控制模型生成内容的随机性。seed参数取值范围是[0, 2147483647]。
如果不提供，则算法自动生成一个随机数作为种子。如果您希望生成内容保持相对稳定，请使用相同的seed参数值。
watermark bool （可选）
是否添加水印标识，水印位于图片右下角，文案为“AI生成”。
false：默认值，不添加水印。
true：添加水印。
响应参数

成功响应异常响应
 
{
    "output": {
        "task_status": "PENDING",
        "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx"
    },
    "request_id": "4909100c-7b5a-9f92-bfe5-xxxxxx"
}
output object
任务输出信息。
属性
task_id string
任务ID。
task_status string
任务状态。
枚举值
PENDING：任务排队中
RUNNING：任务处理中
SUCCEEDED：任务执行成功
FAILED：任务执行失败
CANCELED：任务取消成功
UNKNOWN：任务不存在或状态未知
request_id string
请求唯一标识。可用于请求明细溯源和问题排查。
code string
请求失败的错误码。请求成功时不会返回此参数，详情请参见错误信息。
message string
请求失败的详细信息。请求成功时不会返回此参数，详情请参见错误信息。
步骤2：根据任务ID查询结果

GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}

请求参数

查询任务结果
您需要将86ecf553-d340-4e21-xxxxxxxxx替换为真实的task_id。
 
curl -X GET \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
https://dashscope.aliyuncs.com/api/v1/tasks/86ecf553-d340-4e21-xxxxxxxxx
请求头（Headers）

Authorization string（必选）
请求身份认证。接口使用阿里云百炼API-Key进行身份认证。示例值：Bearer d1xxx2a。
URL路径参数（Path parameters）

task_id string（必选）
任务ID。
响应参数

任务执行成功任务执行失败任务部分失败
任务数据（如任务状态、图像URL等）仅保留24小时，超时后会被自动清除。请您务必及时保存生成的图像。
 
{
    "request_id": "eeef0935-02e9-9742-bb55-xxxxxx",
    "output": {
        "task_id": "a425c46f-dc0a-400f-879e-xxxxxx",
        "task_status": "SUCCEEDED",
        "submit_time": "2025-02-21 17:56:31.786",
        "scheduled_time": "2025-02-21 17:56:31.821",
        "end_time": "2025-02-21 17:56:42.530",
        "results": [
            {
                "url": "https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/aaa.png"
            }
        ],
        "task_metrics": {
            "TOTAL": 1,
            "SUCCEEDED": 1,
            "FAILED": 0
        }
    },
    "usage": {
        "image_count": 1
    }
}
output object
任务输出信息。
属性
task_id string
任务ID。
task_status string
任务状态。
枚举值
PENDING：任务排队中
RUNNING：任务处理中
SUCCEEDED：任务执行成功
FAILED：任务执行失败
CANCELED：任务取消成功
UNKNOWN：任务不存在或状态未知
submit_time string
任务提交时间。
scheduled_time string
任务执行时间。
end_time string
任务完成时间。
results array object
任务结果列表，包括图像URL、部分任务执行失败报错信息等。
数据结构
task_metrics object
任务结果统计。
属性
TOTAL integer
总的任务数。
SUCCEEDED integer
任务状态为成功的任务数。
FAILED integer
任务状态为失败的任务数。
code string
请求失败的错误码。请求成功时不会返回此参数，详情请参见错误信息。
message string
请求失败的详细信息。请求成功时不会返回此参数，详情请参见错误信息。
usage object
输出信息统计。只对成功的结果计数。
属性
image_count integer
模型生成图片的数量。
request_id string
请求唯一标识。可用于请求明细溯源和问题排查。
DashScope SDK调用

请先确认已安装最新版DashScope SDK，否则可能导致运行报错。

DashScope SDK目前已支持Python和Java。

SDK与HTTP接口的参数名基本一致，参数结构根据不同语言的SDK封装而定。参数说明可参考HTTP调用。

由于视频模型处理时间较长，底层服务采用异步方式提供。SDK在上层进行了封装，支持同步、异步两种调用方式。

通用图像编辑模型大约需要5-15秒。实际耗时取决于排队任务数量和网络状况，请您在获取结果时耐心等待。
Python SDK调用

使用Python SDK处理图像文件时，支持传入文件的公网URL或本地文件路径。两种方式二选一即可。

文件公网URL：URL 需为公网可访问地址，支持 HTTP 或 HTTPS 协议。您也可在此获取临时公网URL。
本地文件路径：支持传入文件的绝对路径和相对路径。请参考下表，传入合适的文件路径。
系统
传入的文件路径
示例（绝对路径）
示例（相对路径）
Linux或macOS系统
file://{文件的绝对路径或相对路径}
file:///home/images/test.png
file://./images/test.png
Windows系统
file://D:/images/test.png
file://./images/test.png
同步调用异步调用
请求示例

 
import os
from http import HTTPStatus
# dashscope sdk >= 1.23.4
from dashscope import ImageSynthesis

# 从环境变量中获取 DashScope API Key（即阿里云百炼平台 API key）
api_key = os.getenv("DASHSCOPE_API_KEY")

# ========== 图像输入方式（二选一）==========
# 【方式一】使用公网图片 URL
mask_image_url = "http://wanx.alicdn.com/material/20250318/description_edit_with_mask_3_mask.png"
base_image_url = "http://wanx.alicdn.com/material/20250318/description_edit_with_mask_3.jpeg"

# 【方式二】使用本地文件路径（file://+文件路径）
# 使用绝对路径
# mask_image_url = "file://" + "/path/to/your/mask_image.png"     # Linux/macOS
# base_image_url = "file://" + "C:/path/to/your/base_image.jpeg"  # Windows
# 或使用相对路径
# mask_image_url = "file://" + "./mask_image.png"                 # 以实际路径为准
# base_image_url = "file://" + "./base_image.jpeg"                # 以实际路径为准

def sample_sync_call_imageedit():
    print('please wait...')
    rsp = ImageSynthesis.call(api_key=api_key,
                              model="wanx2.1-imageedit",
                              function="description_edit_with_mask",
                              prompt="陶瓷兔子拿着陶瓷小花",
                              mask_image_url=mask_image_url,
                              base_image_url=base_image_url,
                              n=1)
    assert rsp.status_code == HTTPStatus.OK

    print('response: %s' % rsp)
    if rsp.status_code == HTTPStatus.OK:
        for result in rsp.output.results:
            print("---------------------------")
            print(result.url)
    else:
        print('sync_call Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))

if __name__ == '__main__':
    sample_sync_call_imageedit()
响应示例

url 有效期24小时，请及时下载图像。
 
{
    "status_code": 200,
    "request_id": "dc41682c-4e4a-9010-bc6f-xxxxxx",
    "code": null,
    "message": "",
    "output": {
        "task_id": "6e319d88-a07a-420c-9493-xxxxxx",
        "task_status": "SUCCEEDED",
        "results": [
            {
                "url": "https://dashscope-result-wlcb-acdr-1.oss-cn-wulanchabu-acdr-1.aliyuncs.com/xxx.png?xxxxxx"
            }
        ],
        "submit_time": "2025-05-26 14:58:27.320",
        "scheduled_time": "2025-05-26 14:58:27.339",
        "end_time": "2025-05-26 14:58:39.170",
        "task_metrics": {
            "TOTAL": 1,
            "SUCCEEDED": 1,
            "FAILED": 0
        }
    },
    "usage": {
        "image_count": 1
    }
}
Java SDK调用

使用Java SDK处理图像文件时，支持传入文件的公网URL或本地文件路径。两种方式二选一即可。

文件公网URL：URL 需为公网可访问地址，支持 HTTP 或 HTTPS 协议。您也可在此获取临时公网URL。
本地文件路径：仅支持传入文件的绝对路径。请参考下表，传入合适的文件路径。
系统
传入的文件路径
示例
Linux或macOS系统
file://{文件的绝对路径}
file:///home/images/test.png
Windows系统
file:///{文件的绝对路径}
file:///D:/images/test.png
同步调用异步调用
请求示例

 
// Copyright (c) Alibaba, Inc. and its affiliates.

// dashscope sdk >= 2.20.1
import com.alibaba.dashscope.aigc.imagesynthesis.ImageSynthesis;
import com.alibaba.dashscope.aigc.imagesynthesis.ImageSynthesisParam;
import com.alibaba.dashscope.aigc.imagesynthesis.ImageSynthesisResult;
import com.alibaba.dashscope.exception.ApiException;
import com.alibaba.dashscope.exception.NoApiKeyException;
import com.alibaba.dashscope.utils.JsonUtils;

import java.util.HashMap;
import java.util.Map;

public class ImageEditSync {

    // 从环境变量中获取 DashScope API Key（即阿里云百炼平台 API 密钥）
    static String apiKey = System.getenv("DASHSCOPE_API_KEY");

    /**
     * 图像输入方式（二选一）
     *
     * 【方式一】公网URL
     */
    static String maskImageUrl = "http://wanx.alicdn.com/material/20250318/description_edit_with_mask_3_mask.png";
    static String baseImageUrl = "http://wanx.alicdn.com/material/20250318/description_edit_with_mask_3.jpeg";

    /**
     * 【方式二】本地文件路径（file://+绝对路径 or file:///+绝对路径）
     */
    // static String maskImageUrl = "file://" + "/your/path/to/mask_image.png";     // Linux/macOS
    // static String baseImageUrl = "file:///" + "C:/your/path/to/base_image.png";  // Windows

    public static void syncCall() {
        // 设置parameters参数
        Map<String, Object> parameters = new HashMap<>();
        parameters.put("prompt_extend", true);

        ImageSynthesisParam param =
                ImageSynthesisParam.builder()
                        .apiKey(apiKey)
                        .model("wanx2.1-imageedit")
                        .function(ImageSynthesis.ImageEditFunction.DESCRIPTION_EDIT_WITH_MASK)
                        .prompt("陶瓷兔子拿着陶瓷小花")
                        .maskImageUrl(maskImageUrl)
                        .baseImageUrl(baseImageUrl)
                        .n(1)
                        .size("1024*1024")
                        .parameters(parameters)
                        .build();

        ImageSynthesis imageSynthesis = new ImageSynthesis();
        ImageSynthesisResult result = null;
        try {
            System.out.println("---sync call, please wait a moment----");
            result = imageSynthesis.call(param);
        } catch (ApiException | NoApiKeyException e){
            throw new RuntimeException(e.getMessage());
        }
        System.out.println(JsonUtils.toJson(result));
    }

    public static void main(String[] args) {
        syncCall();
    }
}
响应示例

url 有效期24小时，请及时下载图像。
 
{
    "request_id": "bf6c6361-f0fc-949c-9d60-xxxxxx",
    "output": {
        "task_id": "958db858-153b-4c81-b243-xxxxxx",
        "task_status": "SUCCEEDED",
        "results": [
            {
                "url": "https://dashscope-result-wlcb-acdr-1.oss-cn-wulanchabu-acdr-1.aliyuncs.com/xxx.png?xxxxxx"
            }
        ],
        "task_metrics": {
            "TOTAL": 1,
            "SUCCEEDED": 1,
            "FAILED": 0
        }
    },
    "usage": {
        "image_count": 1
    }
}
错误码

如果模型调用失败并返回报错信息，请参见错误信息进行解决。

此API还有特定状态码，具体如下所示。

HTTP状态码
接口错误码（code）
接口错误信息（message）
含义说明
HTTP状态码
接口错误码（code）
接口错误信息（message）
含义说明
400
InvalidParameter
InvalidParameter
请求参数不合法。
400
IPInfringementSuspect
Input data is suspected of being involved in IP infringement.
输入数据（如提示词或图像）涉嫌知识产权侵权。请检查输入，确保不包含引发侵权风险的内容。
400
DataInspectionFailed
Input data may contain inappropriate content.
输入数据（如提示词或图像）可能包含敏感内容。请修改输入后重试。
500
InternalError
InternalError
服务异常。请先尝试重试，排除偶发情况。
图像访问配置

配置域名白名单：确保业务系统可访问图像链接

模型生成的图像存储于阿里云OSS，每张图像会被分配一个OSS链接，如https://dashscope-result-xx.oss-cn-xxxx.aliyuncs.com/xxx.png。OSS链接允许公开访问，您可以使用此链接查看或者下载图片，链接仅在 24 小时内有效。

特别注意的是，如果您的业务对安全性要求较高，无法访问阿里云OSS链接，您需要单独配置外网访问白名单。请将以下域名添加到您的白名单中，以便顺利访问图片链接。

 
# OSS域名列表
dashscope-result-bj.oss-cn-beijing.aliyuncs.com
dashscope-result-hz.oss-cn-hangzhou.aliyuncs.com
dashscope-result-sh.oss-cn-shanghai.aliyuncs.com
dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.com
dashscope-result-zjk.oss-cn-zhangjiakou.aliyuncs.com
dashscope-result-sz.oss-cn-shenzhen.aliyuncs.com
dashscope-result-hy.oss-cn-heyuan.aliyuncs.com
dashscope-result-cd.oss-cn-chengdu.aliyuncs.com
dashscope-result-gz.oss-cn-guangzhou.aliyuncs.com
dashscope-result-wlcb-acdr-1.oss-cn-wulanchabu-acdr-1.aliyuncs.com
常见问题

图像模型的通用问题请参见常见问题文档，包括以下内容：模型计费与限流规则、接口高频报错解决方法等。