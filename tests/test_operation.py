import brownie
from brownie import Contract


def test_operation(accounts, token, vault, strategy, strategist, amount):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    assert token.balanceOf(vault.address) == amount

    # harvest
    strategy.harvest()
    print(f'\n [normal harvest]')
    print(f'token balance on strategy: {token.balanceOf(strategy.address)}')

    # tend()
    strategy.tend()

    # withdrawal
    vault.withdraw({"from": accounts[0]})
    assert token.balanceOf(accounts[0]) != 0


def test_emergency_exit(accounts, token, vault, strategy, strategist, amount):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    strategy.harvest()
    print(f'\n [normal harvest]')
    print(f'token balance on strategy: {token.balanceOf(strategy.address)}')

    # set emergency and exit
    strategy.setEmergencyExit()
    strategy.harvest()
    print(f'\n [harvest after set emergency exit]')
    print(f'token balance on strategy: {token.balanceOf(strategy.address)}')
    assert token.balanceOf(strategy.address) < amount


def test_profitable_harvest(accounts, token, vault, strategy, strategist, amount):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    assert token.balanceOf(vault.address) == amount

    # harvest
    strategy.harvest()
    print(f'\n [normal harvest]')
    print(f'token balance on strategy: {token.balanceOf(strategy.address)}')

    # You should test that the harvest method is capable of making a profit.
    # TODO: uncomment the following lines.
    # strategy.harvest()
    # chain.sleep(3600 * 24)
    # assert token.balanceOf(strategy.address) > amount


def test_change_debt(gov, token, vault, strategy, strategist, amount):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": gov})
    vault.deposit(amount, {"from": gov})
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    strategy.harvest()

    print(f'\n [update strategy debt ratio: 5_000]')
    print(f'token balance on strategy: {token.balanceOf(strategy.address)}')

    vault.updateStrategyDebtRatio(strategy.address, 10_000, {"from": gov})
    strategy.harvest()
    print(f'\n [update strategy debt ratio back: 10_000]')
    print(f'token balance on strategy: {token.balanceOf(strategy.address)}')

    # In order to pass this tests, you will need to implement prepareReturn.
    # TODO: uncomment the following lines.
    # vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    # assert token.balanceOf(strategy.address) == amount / 2


def test_sweep(gov, vault, strategy, token, amount, weth, weth_amout):
    # Strategy want token doesn't work
    token.transfer(strategy, amount, {"from": gov})
    assert token.address == strategy.want()
    assert token.balanceOf(strategy) > 0
    with brownie.reverts("!want"):
        strategy.sweep(token, {"from": gov})

    # Vault share token doesn't work
    with brownie.reverts("!shares"):
        strategy.sweep(vault.address, {"from": gov})

    # TODO: If you add protected tokens to the strategy.
    # Protected token doesn't work
    # with brownie.reverts("!protected"):
    #     strategy.sweep(strategy.protectedToken(), {"from": gov})

    weth.transfer(strategy, weth_amout, {"from": gov})
    assert weth.address != strategy.want()
    assert weth.balanceOf(gov) == 0
    strategy.sweep(weth, {"from": gov})
    assert weth.balanceOf(gov) == weth_amout


def test_triggers(gov, vault, strategy, token, amount, weth, weth_amout):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": gov})
    vault.deposit(amount, {"from": gov})
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})

    print(f'harvest trigger: {strategy.harvestTrigger(0)}')
    print(f'tend trigger : {strategy.tendTrigger(0)}')

    strategy.harvest()

    print(f'harvest trigger: {strategy.harvestTrigger(0)}')
    print(f'tend trigger : {strategy.tendTrigger(0)}')
