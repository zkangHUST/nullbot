from nonebot import on_command, CommandSession
from nullbot.utils.deco import group_only, superuser_only
from nullbot.utils.helpers import parse_cq_at
from spideroj.config import PLATFORM_URLS
from spideroj.mongo import DataManager
import re


@on_command('init_db', only_to_me=False, shell_like=True)
@group_only
@superuser_only
async def handle_init_db(session: CommandSession):
    argv = session.args['argv']
    cleanup = True if '-c' in argv else False
    
    msg = '正在初始化数据库...'
    if cleanup:
        msg += '(重置)'
    await session.send(msg)

    group_id = session.ctx['group_id']
    members = await session.bot.get_group_member_list(group_id=group_id)

    dm = DataManager(group_id)
    success = dm.init(members, cleanup)

    await session.send('成功导入{}位成员信息'.format(success))


@on_command('reset_db')
@group_only
@superuser_only
async def handle_reset_db(session: CommandSession):
    group_id = session.ctx['group_id']
    DataManager(group_id).reset()

    await session.send('数据库已重置')


@on_command('register', only_to_me=False)
@group_only
async def handle_register(session: CommandSession):
    example = "\n".join([f"{oj}: {url.format('<id>')}" for oj, url in PLATFORM_URLS.items()])
    USAGE = """用法： 
register <your OJ profile url>

目前支持的OJ平台：
""" + example + """

示例：
register https://leetcode.com/nuullll
"""

    url = session.current_arg_text.strip()

    if not url:
        await session.finish(USAGE)
        return
    
    url = url.split()[0]

    platform = ''
    user_id = ''
    for oj, template in PLATFORM_URLS.items():
        m = re.search(template.format('([a-zA-Z0-9_-]+)'), url)
        if m:
            platform = oj
            user_id = m.group(1)
            break
    
    if not user_id:
        await session.send("输入有误！")
        await session.finish(USAGE)
        return
    
    group_id = session.ctx['group_id']
    qq_id = session.ctx['user_id']
    dm = DataManager(group_id)

    binded, bind_qq = dm.is_account_binded(user_id, platform)
    if binded:
        if bind_qq == qq_id:
            await session.finish(f"您已绑定{user_id}@{platform}，请勿重复操作。")
        else:
            await session.finish(f"绑定失败，{user_id}@{platform}已被用户[CQ:at,qq={bind_qq}]绑定！")
        return

    ok = await dm.get_and_save_user_summary(qq_id, user_id, platform)

    if not ok:
        await session.send("ID错误或网络错误！请检查后重试。")
        await session.finish(USAGE)
        return
    
    if not dm.bind_account(qq_id, user_id, platform):
        await session.finish("绑定失败，代码线程不安全。")
        return

    await session.send(f"{user_id}@{platform}绑定成功！")


@on_command('deregister', only_to_me=False, shell_like=True)
@group_only
async def handle_deregister(session: CommandSession):
    USAGE = """用法： 
deregister [-a] [platform] [user_id]

可选参数：
-a 解绑本人所有OJ平台账号

示例：
deregister -a
deregister leetcodecn nuullll
"""
    # args
    argv = session.args['argv']
    if not argv:
        await session.finish(USAGE)
        return

    rm_all = True if '-a' in argv else False

    group_id = session.ctx['group_id']
    qq_id = session.ctx['user_id']

    dm = DataManager(group_id)
    if rm_all:
        candidates = dm.query_binded_accounts(qq_id)
    else:
        try:
            platform = argv[0]
            user_id = argv[1]
        except:
            await session.send("参数有误！")
            await session.finish(USAGE)
            return
        
        binded, bind_qq = dm.is_account_binded(user_id, platform)
        if not binded or bind_qq != qq_id:
            await session.finish("账号不存在，解绑失败。@我 accounts 查询已绑定账号。")
            return
        
        candidates = [(user_id, platform)]
    
    for u, p in candidates:
        dm.remove_account(qq_id, u, p)
    
    await session.finish("解绑成功。")


@on_command('accounts')
@group_only
async def handle_accounts(session: CommandSession):
    group_id = session.ctx['group_id']
    qq_id = session.ctx['user_id']

    dm = DataManager(group_id)
    accounts = dm.query_binded_accounts(qq_id)

    if accounts:
        msg = '已绑定账号：\n' + '\n'.join([u+'@'+p for u, p in accounts])
    else:
        msg = '并没有绑定账号。'
    
    await session.send(msg, at_sender=True)


@on_command('register_for', only_to_me=False, shell_like=True)
@group_only
@superuser_only
async def handle_register_for(session: CommandSession):
    group_id = session.ctx['group_id']
    
    argv = session.args['argv']
    qq_id, url = argv

    try:
        if qq_id.isnumeric():
            qq_id = int(qq_id)
        else:
            # infer CQ code
            qq_id = parse_cq_at(qq_id)
    except:
        await session.finish('参数错误！')
        return
    
    dm = DataManager(group_id)

    platform = ''
    user_id = ''
    for oj, template in PLATFORM_URLS.items():
        m = re.search(template.format('([a-zA-Z0-9_-]+)'), url)
        if m:
            platform = oj
            user_id = m.group(1)
            break
    
    if not user_id:
        await session.send("输入有误！")
        await session.finish(USAGE)
        return

    binded, bind_qq = dm.is_account_binded(user_id, platform)
    if binded:
        if bind_qq == qq_id:
            await session.finish(f"您已绑定{user_id}@{platform}，请勿重复操作。")
        else:
            await session.finish(f"绑定失败，{user_id}@{platform}已被用户[CQ:at,qq={bind_qq}]绑定！")
        return

    ok = await dm.get_and_save_user_summary(qq_id, user_id, platform)

    if not ok:
        await session.send("ID错误或网络错误！请检查后重试。")
        await session.finish(USAGE)
        return
    
    if not dm.bind_account(qq_id, user_id, platform):
        await session.finish("绑定失败，代码线程不安全。")
        return

    await session.send(f"{user_id}@{platform}绑定成功！")