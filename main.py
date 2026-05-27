from pycardano import Address, AssetName, AuxiliaryData, BlockFrostChainContext, HDWallet, InvalidHereAfter, Metadata, MultiAsset, Network, PaymentExtendedSigningKey, ScriptPubkey, StakeExtendedSigningKey, Transaction, TransactionBody, TransactionBuilder, TransactionInput, TransactionOutput, TransactionWitnessSet, UTxO, Value, BlockFrostChainContext, VerificationKey, ScriptAll , VerificationKeyHash
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




def derive_keys_from_hd_wallet(hd: HDWallet):
    payment_hd = hd.derive_from_path("m/1852'/1815'/0'/0/0")
    staking_hd = hd.derive_from_path("m/1852'/1815'/0'/2/0")
    
    payment_key = PaymentExtendedSigningKey.from_hdwallet(
        payment_hd
    )
    stake_key = StakeExtendedSigningKey.from_hdwallet(
        staking_hd
    )

    return payment_key, stake_key



def send_ada(input_address: Address, destination_address: Address, payment_key: PaymentExtendedSigningKey, amount: Value):
    # transformar função para enviar ada
    ctx = load_blockfrost_context()
    builder = TransactionBuilder(ctx)
    builder.add_input_address(input_address)
    builder.add_output(TransactionOutput(
        destination_address,
        amount
    ))

    tx_signed = builder.build_and_sign([payment_key], change_address=input_address)

    return ctx.submit_tx(tx_signed)


def add_witness_set(tx_body: TransactionBody, metadata: dict | None = None) -> Transaction:
    return Transaction(
        transaction_body=tx_body,
        transaction_witness_set=TransactionWitnessSet(),
        auxiliary_data=AuxiliaryData(Metadata(metadata)) if metadata is not None else None
    )



def build_tx_body(input_address: Address, destination_addr: Address, amount: Value, metadata: dict | None = None) -> TransactionBody:
    ctx = load_blockfrost_context()
    builder = TransactionBuilder(ctx)
    builder.add_input_address(input_address)
    builder.add_output(TransactionOutput(
        destination_addr,
        amount
    ))
    if metadata is not None:
        builder.auxiliary_data = AuxiliaryData(Metadata(metadata))

    return builder.build(change_address=input_address)


def build_tx_for_multi_sig(input_address: Address, destination_addr: Address, amount: Value, native_script: ScriptAll, payment_key: PaymentExtendedSigningKey):
    ctx = load_blockfrost_context()
    builder = TransactionBuilder(ctx)

    utxos = ctx.utxos(input_address)
    builder.add_input(utxos[0])  # Adicione o UTxO correto aqui

    builder.native_scripts = [native_script]
    builder.required_signers = [script.key_hash for script in native_script.native_scripts]
    builder.add_output(TransactionOutput(
        destination_addr,
        amount
    ))

    return builder.build_and_sign([payment_key], change_address=input_address)
    


def build_tx_mint_cip25(
        input_address: Address, 
        destination_addr: Address, 
        payment_key: PaymentExtendedSigningKey, 
        asset_name: AssetName,
        ada_amount: int,
        native_token_amount: int,
        native_script: ScriptAll):
    ctx = load_blockfrost_context()

    policy_id = native_script.hash()
    print(f"Policy ID: {policy_id}")

    metadata = {
        721: {
            policy_id.payload.hex(): {
                asset_name.payload.decode(): {
                    "name": "My Little Token",
                    "image": "ipfs://QmRhTTbUrPYEw3mJGGhQqQST9k86v1DPBiTTWJGKDJsVFw",
                    "description": "This is a test token minted using pycardano and a native script"
                }
            }
        }
    }


    mytoken = MultiAsset.from_primitive(
        {
            policy_id.payload: {  # Use policy ID created from above. We can't use policy_id here because policy_id's type  # is ScriptHash, which is not a primitive type. Instead, we use policy_id.payload (bytes)
                asset_name.payload: native_token_amount,  # Name of our NFT1  # Quantity of this NFT
            }
        }
    )



    builder = TransactionBuilder(ctx)
    builder.add_input_address(input_address)
    #builder.mint = MultiAsset(
    #     {policy_id: {asset_name: native_token_amount}}
    # )
    builder.mint = mytoken
    builder.auxiliary_data = AuxiliaryData(Metadata(metadata))
    builder.native_scripts = [native_script]
    builder.add_output(TransactionOutput(
        destination_addr,
        Value(ada_amount, mytoken)
    ))

    tx_signed = builder.build_and_sign([payment_key], change_address=input_address)
    print(f"Transaction ID: {tx_signed.to_cbor_hex()}")
    
    
    return ctx.submit_tx(tx_signed)


def main():
    
    destination_addr = Address.from_primitive(
        "CHAVE PARA ENVIAR ADA E TOKENS")



    hd = load_wallet()
    payment_key, stake_key = derive_keys_from_hd_wallet(hd)

    address = Address(
        payment_part=payment_key.to_verification_key().hash(),
        staking_part=stake_key.to_verification_key().hash(),
        network=Network.TESTNET
    )




    #tx_id = send_ada(address, destination_addr, payment_key, Value(100_000_000))


    # metadata = {
    #     674: {
    #         "msg": "Hello, Cardano!"
    #     }
    # }
    # tx_body = build_tx_body(address, destination_addr, Value(100_000_000), metadata)
    # #print(tx_body.to_cbor_hex())
    # unsigned_tx = add_witness_set(tx_body, metadata)
    # print(unsigned_tx.to_cbor_hex())

    #print(f"Transaction submitted with ID: {tx_id}")

    

    # multi sig e native script
    vkey_hash_local = payment_key.to_verification_key().hash()
    vkey_hash_eternl = destination_addr.payment_part


    ctx = load_blockfrost_context()

    expiry_slot = ctx.last_block_slot + 10800
    native_script = ScriptAll(
        [
            ScriptPubkey(vkey_hash_local),
            #ScriptPubkey(vkey_hash_eternl)
            InvalidHereAfter(expiry_slot)
        ]
    )

    # script_address = Address(
    #     payment_part=native_script.hash(),
    #     network=Network.TESTNET
    # )
    # print(f"Script address: {script_address}")

    # enviar ada para o script address
    #tx_id = send_ada(address, script_address, payment_key, Value(100_000_000))
    #print(f"Transaction submitted with ID: {tx_id}")

    # tx = build_tx_for_multi_sig(script_address, destination_addr, Value(5_000_000), native_script, payment_key)
    # print(tx.to_cbor_hex())



    asset_name = AssetName(b"MyLittleToken")

    tx_id = build_tx_mint_cip25(
        address, destination_addr, payment_key, asset_name, 5_000_000, 10, native_script
        )
    
    print(tx_id)





if __name__ == "__main__":
    main()
