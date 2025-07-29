from nonebot_plugin_orm import AsyncSession, get_session

from ..repository import TransactionRepository


async def get_transaction_history(
    account_id: str,
    limit: int = 100,
    session: AsyncSession | None = None,
):
    """获取一个用户的交易记录

    Args:
        session (AsyncSession | None, optional): 异步数据库会话
        account_id (str): 用户UUID(应自行处理)
        limit (int, optional): 数据条数. Defaults to 100.

    Returns:
        Sequence[Transaction]: 记录列表
    """
    if session is None:
        session = get_session()
    return await TransactionRepository(session).get_transaction_history(
        account_id, limit
    )


async def remove_transaction(
    transaction_id: str,
    session: AsyncSession | None = None,
    fail_then_throw: bool = False,
) -> bool:
    """删除交易记录

    Args:
        transaction_id (str): 交易ID
        session (AsyncSession | None, optional): 异步数据库会话. Defaults to None.
        fail_then_throw (bool, optional): 如果失败则抛出异常. Defaults to False.

    Returns:
        bool: 是否成功
    """
    if session is None:
        session = get_session()
    async with session:
        try:
            await TransactionRepository(session).remove_transaction(transaction_id)
            return True
        except Exception:
            if fail_then_throw:
                raise
            return False
