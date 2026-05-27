# from pycardano import Address, HDWallet, Network, PaymentExtendedSigningKey, StakeExtendedSigningKey, TransactionBuilder, TransactionOutput, BlockFrostChainContext, BlockFrostKeyContext
# # from pycardano.broadcaster import load_broadcaster_context 
# import os


# def load_wallet():
   
#    # criar a hd wallet  -  
#     with open("seed.txt", "r") as f:
#         hd = HDWallet.from_mnemonic(f.read().strip())  
#         print(hd.public_key.hex())   
#     return hd 
#         # skey = f.read().strip()
# def main():        
    
   
#     hd  =  load_wallet()
#     payment = hd.derive_from_path("m/1852'/1815'/0'/0/0")
#     staking = hd.derive_from_path("m/1852'/1815'/0'/2/0")

#     payment_key = PaymentExtendedSigningKey.from_hdwallet(payment)
#     stake_key = StakeExtendedSigningKey.from_hdwallet(staking)
    
#     # payment_key.sign(b"teste")

#     address = Address(
   
#             payment_part=payment_key.to_verification_key().hash(),
#             staking_part= stake_key.to_verification_key().hash(),
#             network = Network.TESTNET )

#     print(address)

#     ctx = load_broadcaster_context()
#     builder = TransactionBuilder(ctx)
#     builder.add_input(address)
#     builder.add_output(TransactionOutput(address, 10_000_000))

#     tx_signed = builder.build_and_sign([payment_key], change_address=address)
#     # print(tx_signed.to_cbor())
    
#     tx_id = ctx.submit_tx(tx_signed)

                            
#     # print("Skey:", skey)
#     # address = Address.from_primitive("CHAVE") 
    
#     # # print("Address:", address) # endereço
#     # # raw = bytes(address).hex() # hexadecimal
#     # # print("Raw:", raw) # 

#     # print(address.payment_part) # pagamento
#     # print(address.staking_part) # delegação
    
#     # carteira deterministoca e hierarquica (HD Wallet) - BIP32, BIP44, BIP84

#     # 


# # ler a carteira do arquivo  

# def load_blockchain_context() -> BlockFrostKeyContext:
#     bf_key = os.environ.get("BLOCKFROST_KEY")
#     assert bf_key is not None, "Please set the BLOCKFROST_KEY environment variable"
#     return BlockFrostChainContext(bf_key, Network.TESTNET)

# #  transação é um array com trasarion body -  valor boleano V ou F e o dado auxiliar -  se for V, o dado é a assinatura, se for F, o dado é o script ou a chave pública.



# if __name__ == "__main__":
#     main()

from pycardano import Address, BlockFrostChainContext, HDWallet, Network, PaymentExtendedSigningKey, StakeExtendedSigningKey, TransactionBuilder, TransactionOutput, Value, BlockFrostChainContext
import os


def load_wallet():
    # ler a carteira do arquivo e retornar o HDWallet correspondente
    with open("seed.txt", "r") as f:
        hd = HDWallet.from_mnemonic(f.read().strip())
    
    return hd


def load_blockfrost_context() -> BlockFrostChainContext:
    bf_key = os.environ.get("BLOCKFROST_KEY")

    assert bf_key is not None, "BLOCKFROST_KEY environment variable not set"
    
    return BlockFrostChainContext(bf_key)


def main():
    
    addr = Address.from_primitive("CHAVE")
    # raw = bytes(addr)

    # print(raw.hex())

    # print(addr.network)
    # print(addr.payment_part)
    # print(addr.staking_part)




    hd = load_wallet()
    payment_hd = hd.derive_from_path("m/1852'/1815'/0'/0/0")
    staking_hd = hd.derive_from_path("m/1852'/1815'/0'/2/0")


    
    payment_key = PaymentExtendedSigningKey.from_hdwallet(
        payment_hd
    )
    stake_key = StakeExtendedSigningKey.from_hdwallet(
        staking_hd
    )

    address = Address(
        payment_part=payment_key.to_verification_key().hash(),
        staking_part=stake_key.to_verification_key().hash(),
        network=Network.TESTNET
    )


    print(address)





    ctx = load_blockfrost_context()
    builder = TransactionBuilder(ctx)
    builder.add_input_address(address)
    builder.add_output(TransactionOutput(
        addr,
        Value(100_000_000)
    ))

    tx_signed = builder.build_and_sign([payment_key], change_address=address)
    #print(tx_signed.to_cbor().hex())

    tx_id = ctx.submit_tx(tx_signed)
    print(f"Transaction submitted with ID: {tx_id}")





if __name__ == "__main__":
    main()
