Title: ZHIPU AI OPEN PLATFORM

URL Source: https://bigmodel.cn/dev/api/image-model/cogview

Markdown Content:
CogView-4
---------

Designed for image generation tasks, it enables precise and personalized AI visual expression through rapid, accurate interpretation of user text descriptions.

*   Model codes: cogview-4-250304 `latest`, cogview-4, cogview-3-flash；
*   Learn about [cogview-4-250304](https://www.bigmodel.cn/dev/howuse/cogview) model features；
*   Check [product pricing](https://www.bigmodel.cn/pricing) - CogView-4 series models: ¥0.06 per generation；
*   Experience model capabilities at the [Demo Center](https://www.bigmodel.cn/login?redirect=%2Ftrialcenter%2Fmodeltrial%3FmodelCode%3Dcogview-4-250304)；
*   View model [rate limits](https://www.bigmodel.cn/login?redirect=%2Fusercenter%2Fcorporateequity)；
*   Check your [API Key](https://www.bigmodel.cn/login?redirect=%2Fusercenter%2Fproj-mgmt%2Fapikeys)；

Synchronous Call
----------------

### Interface Request

| Transfer Method | HTTPS |
| --- | --- |
| Request URL | https://open.bigmodel.cn/api/paas/v4/images/generations |
| Call Method | Synchronous call, wait for the model to complete execution and return the final result |
| Character Encoding | UTF-8 |
| Interface Request Format | JSON |
| Response Format | JSON |
| Interface Request Type | POST |
| Development Language | Any development language that can initiate http requests |

### Request Parameters

| Parameter Name | Type | Required | Description |
| --- | --- | --- | --- |
| model | String | Yes | Model code |
| prompt | String | Yes | Text description of the desired image |
| quality | String | No | Image generation quality, default is standard. hd: Generates more refined, detailed images with higher overall consistency, taking approximately 20 seconds. standard: Quickly generates images, suitable for scenarios requiring faster generation speed, taking approximately 5-10 seconds. This parameter is only supported by cogview-4-250304. |
| size | String | No | Image size, only supported by cogview-3-plus. Optional range: [1024x1024, 768x1344, 864x1152, 1344x768, 1152x864, 1440x720, 720x1440], default is 1024x1024. |
| user_id | String | No | Unique ID of the end user, assisting the platform in intervening in violations, illegal and不良information generation, or other misuse by the end user. ID length requirement: at least 6 characters, up to 128 characters. |

### Response Parameters

| Parameter Name | Type | Parameter Description |
| --- | --- | --- |
| created | String | The request creation time, which is a Unix timestamp in seconds. |
| data | List | An array containing the generated image URL. Currently, the array contains only one image. |
| url | String | Image link. The temporary link of the image is valid for 30 days. Please transfer and save the image in a timely manner. |
| content_filter | List | Return information related to content security. |
| role | String | Security effective links, including role = assistant model reasoning, role = user user input, role = history historical context |
| level | Integer | Severity level 0 - 3, level 0 indicates the most serious, 3 indicates minor |

### Call Example

```
from zhipuai import ZhipuAI
client = ZhipuAI(api_key="") # Enter your own API Key
  
response = client.images.generations(
    model="cogview-4-250304", # Specify the model code to call
    prompt="A cute little kitten",
)

print(response.data[0].url)
```

1

2

3

4

5

6

7

8

9

#### Response Example

```
{
  "created": 1703485556,
  "data": [
      {
          "url": "https://......"
      }
  ]
}
```

1

2

3

4

5

6

7

8