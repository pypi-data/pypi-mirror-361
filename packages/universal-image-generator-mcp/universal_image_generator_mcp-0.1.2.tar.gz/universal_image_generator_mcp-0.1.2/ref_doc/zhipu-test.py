from zhipuai import ZhipuAI
client = ZhipuAI(api_key="5fd2e90642714f7f85b9e2fce37c202f.lLI1o65gADhuoIld") # 请填写您自己的APIKey
  
response = client.images.generations(
    model="cogview-4-250304", #填写需要调用的模型编码
    prompt="一只可爱的小猫咪",
)

print(response.data[0].url)