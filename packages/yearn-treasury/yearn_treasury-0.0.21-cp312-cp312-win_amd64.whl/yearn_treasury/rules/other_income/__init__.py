from decimal import Decimal
from typing import Final

from dao_treasury import TreasuryTx, other_income
from y import Contract, ContractNotVerified, ERC20, Network  # type: ignore [attr-defined]

from yearn_treasury.rules.constants import ZERO_ADDRESS


_POINT_ONE: Final = Decimal("0.1")


@other_income("Airdrop", Network.Mainnet)
def is_airdrop(tx: TreasuryTx) -> bool:
    txhash = tx.hash
    return txhash in {
        "0x327684dab9e3ce61d125b36fe0b59cbfbc8aa5ac7a5b051125ab7cac3b93b90b",
        "0x3424e8a6688c89f7974968213c8c25f3bd8100f78c54475edb001c11a8ad5d21",  # Gnosis SAFE airdrop
        "0xb39f2991fdc2c70b43046be3eac36bff35c21c7f66e2888a52afc3956abae451",  # Gnosis SAFE airdrop
        "0x4923fd32b4eacdc1617700c67176935676ca4d06bbfbb73644730c55534623db",  # Gnosis SAFE airdrop
        "0x5ba604cae0d355835b182fa23c8a58ae695905e69ed08c7cf8a52f3eca889484",  # Gnosis SAFE airdrop
        "0x44f7d3b2030799ea45932baf6049528a059aabd6387f3128993d646d01c8e877",  # TKX
        "0xf2dbe58dffd3bc1476755e9f74e2ae07531579d0a3ea9e2aaac2ef902e080c2a",  # TKX
        "0x8079e9cae847da196dc5507561bc9d1434f765f05045bc1a82df735ec83bc6ec",  # MTV
        "0x037a9cc5baa7d63a11d0f0720ee552bbf4ad85118ee5425220a263695fedbe9f",  # Gnosis SAFE airdrop
        # NOTE: this one was rec'd elsewhere, dumped, and WETH sent to treasury
        "0xc12ded505ea158717890e4ae6e7ab5eb5cb61edbc13dfd125dd0e6f9b1af9477",  # Gnosis SAFE airdrop
        "0x7c086a82b43b2f49db93b76a0698cf86a9c620b3bf924f0003175b04a17455ad",  # PRISMA
    } or (
        # Gnosis SAFE airdrop
        txhash == "0xe8b5a4ebf1f04048f6226b22b2865a33621e88ea255dcea0cfd7a975a3a7e387"
        and tx.log_index == 72
    )


@other_income("aToken Yield", Network.Mainnet)
def is_atoken_yield(tx: TreasuryTx) -> bool:
    return (
        tx.symbol in ("aLEND", "aLINK")
        and tx.from_address.address == ZERO_ADDRESS
        and tx.to_nickname in ("Yearn Treasury", "Yearn Treasury V1")
    )


@other_income("RoboVault Thank You", Network.Fantom)
async def is_robovault_share(tx: TreasuryTx) -> bool:
    """
    After Yearn devs helped robovault with a vulnerability, robovault committed to sending Yearn a portion of their fees.
    """
    if not tx.symbol.startswith("rv") and tx.from_address.is_contract:
        return False

    try:
        strat = await Contract.coroutine(tx.from_address.address)
    except ContractNotVerified:
        return False

    if not hasattr(strat, "vault"):
        return False

    if await strat.vault.coroutine(block_identifier=tx.block) == tx.token:
        return True

    return (
        tx.from_nickname == "Contract: Strategy"
        and tx.symbol == "rv3USDCc"
        and await ERC20(  # type: ignore [call-overload]
            await strat.vault.coroutine(block_identifier=tx.block),
            asynchronous=True,
        ).symbol
        == "rv3USDCb"
    )


@other_income("Cowswap Gas Reimbursement", Network.Mainnet)
def is_cowswap_gas_reimbursement(tx: TreasuryTx) -> bool:
    return (
        tx.symbol == "ETH"
        and tx.from_nickname == "Cowswap Multisig"
        and tx.to_nickname == "yMechs Multisig"
    )


@other_income("USDS Referral Code", Network.Mainnet)
def is_usds_referral_code(tx: TreasuryTx) -> bool:
    """Yearn earns some USDS for referring deposits to Maker"""
    return (
        tx.symbol == "USDS"
        and tx.from_address.address == "0x3C5142F28567E6a0F172fd0BaaF1f2847f49D02F"
    )


@other_income("yETH Application Fee", Network.Mainnet)
def is_yeth_application_fee(tx: TreasuryTx) -> bool:
    return tx.symbol == "yETH" and tx.to_nickname == "Yearn Treasury" and tx.amount == _POINT_ONE


@other_income("yPRISMA Fees", Network.Mainnet)
def is_yprisma_fees(tx: TreasuryTx) -> bool:
    return tx.symbol == "yvmkUSD-A" and tx.from_nickname == "Contract: YPrismaFeeDistributor"
