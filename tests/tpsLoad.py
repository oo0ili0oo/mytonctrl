#!/usr/bin/env python3
# -*- coding: utf_8 -*-l

from sys import path
path.append("/usr/src/mytonctrl/")
from mytoncore import *

Local = MyPyClass(__file__)
ton = MyTonCore()


def Init():
	wallets = list()
	Local.buffer["wallets"] = wallets
	walletsNameList = ton.GetWalletsNameList()
	
	# Create tests wallet
	testsWalletName = "tests_hwallet"
	testsWallet = ton.CreateHighWallet(testsWalletName)

	# Check tests wallet balance
	account = ton.GetAccount(testsWallet.addr)
	local.add_log("wallet: {addr}, status: {status}, balance: {balance}".format(addr=testsWallet.addr, status=account.status, balance=account.balance))
	if account.balance == 0:
		raise Exception(testsWallet.name + " wallet balance is empty.")
	if account.status == "uninit":
		ton.SendFile(testsWallet.bocFilePath, testsWallet)

	# Create wallets
	for i in range(load):
		walletName = "w_" + str(i)
		if walletName not in walletsNameList:
			wallet = ton.CreateWallet(walletName)
		else:
			wallet = ton.GetLocalWallet(walletName)
		wallets.append(wallet)
	#end for

	# Fill up wallets
	buff_wallet = None
	buff_seqno = None
	destList = list()
	for wallet in wallets:
		wallet.account = ton.GetAccount(wallet.addr)
		need = 20 - wallet.account.balance
		if need > 10:
			destList.append([wallet.addr_init, need])
		elif need < -10:
			need = need * -1
			buff_wallet = wallet
			buff_wallet.oldseqno = ton.GetSeqno(wallet)
			ton.MoveGrams(wallet, testsWallet.addr, need, wait=False)
			Local.add_log(testsWallet.name + " <<< " + wallet.name)
	if buff_wallet:
		ton.WaitTransaction(buff_wallet, False)
	#end for

	# Move grams from highload wallet
	ton.MoveGramsFromHW(testsWallet, destList)

	# Activate wallets
	for wallet in wallets:
		if wallet.account.status == "uninit":
			wallet.oldseqno = ton.GetSeqno(wallet)
			ton.SendFile(wallet.bocFilePath)
		Local.add_log(str(wallet.subwallet) + " - OK")
	ton.WaitTransaction(wallets[-1])
#end define

def Work():
	wallets = Local.buffer["wallets"]
	for i in range(load):
		if i + 1 == load:
			i = -1
		#end if
		
		wallet1 = wallets[i]
		wallet2 = wallets[i+1]
		wallet1.oldseqno = ton.GetSeqno(wallet1)
		ton.MoveGrams(wallet1, wallet2.addr, 3.14, wait=False)
		Local.add_log(wallet1.name + " >>> " + wallet2.name)
	ton.WaitTransaction(wallets[-1])
#end define

def General():
	Init()
	while True:
		time.sleep(1)
		Work()
		Local.add_log("Work - OK")
	#end while
#end define



###
### Start test
###
Local = MyPyClass(__file__)
Local.db["config"]["logLevel"] = "info"
Local.Run()

ton = MyTonCore()
local.db["config"]["logLevel"] = "info"
load = 100

Local.StartCycle(General, sec=1)
Sleep()
