from mcp.server.fastmcp import FastMCP
import logging

logger = logging.getLogger('mcp')
settings = {
    'log_level': 'DEBUG'
}
# 初始化mcp服务
mcp = FastMCP('Waybill Intercept Demo', log_level='ERROR', settings=settings)
# 定义工具
@mcp.tool(description="拦截运单号，返回是否拦截及原因")
def intercept_waybill(waybill_no: str) -> dict:
    # mock 逻辑：以A开头的运单号拦截
    if waybill_no.startswith("A"):
        return {"waybill_no": waybill_no, "intercepted": True, "reason": "黑名单运单号"}
    else:
        return {"waybill_no": waybill_no, "intercepted": False, "reason": "正常运单号"}
def run():
    mcp.run(transport='stdio')
if __name__ == '__main__':
   run()