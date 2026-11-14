// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "forge-std/Test.sol";
import "../contracts/PQAccountRegistry.sol";

contract PQMainnetForkTest is Test {
    string constant RPC_URL = "https://mainnet-rpc.rayls.com";
    uint256 constant CHAIN_ID = 72957;

    address constant CONSENSUS_REGISTRY = 0x07E17e17E17e17E17e17E17E17E17e17e17E17e1;
    address constant FEE_AGGREGATOR_PROXY = 0x07E17E17e17E17e17E17e17e17e17e17E17E17E3;
    address constant DELEGATION_POOL = 0x07e17e17e17e17e17e17e17e17E17e17e17e17e9;

    PQAccountRegistry public registry;
    uint256 public forkId;

    address public bank1 = address(0x1111);
    address public bank2 = address(0x2222);

    bytes constant VALID_MLKEM_KEY = new bytes(1184);
    bytes constant VALID_MLKEM_CIPHERTEXT = new bytes(1088);
    bytes32 constant CONFIRMATION_TAG = keccak256("enygma-view-key-confirm-v1:live-mainnet-fork");

    function setUp() public {
        forkId = vm.createSelectFork(RPC_URL);
        PQAccountRegistry.GuardConfig memory guards = PQAccountRegistry.GuardConfig(true, true, true, true);
        registry = new PQAccountRegistry(guards);
    }

    /// @notice Test 1: Verify fork environment, chain ID, and Genesis contract bytecodes
    function test_MainnetFork_ChainStateAndGenesisContractsPresent() public view {
        assertEq(block.chainid, CHAIN_ID, "Forked chainId must match Rayls Mainnet 72957");
        assertTrue(block.gaslimit >= 500_000_000, "Block gas limit must be at least 500M");

        assertEq(CONSENSUS_REGISTRY.code.length, 21929, "ConsensusRegistry bytecode must match canonical 21,929 bytes");
        assertEq(FEE_AGGREGATOR_PROXY.code.length, 122, "FeeAggregatorProxy bytecode must match canonical 122 bytes");
        assertEq(DELEGATION_POOL.code.length, 15790, "DelegationPool bytecode must match canonical 15,790 bytes");
    }

    /// @notice Test 2: Measure live gas of registering an 1,184-byte post-quantum view key on Mainnet fork
    function test_MainnetFork_RegisterMLKEM768Account_GasMeasurement() public {
        uint256 gasBefore = gasleft();
        vm.prank(bank1);
        registry.registerAccount(1, bank1, 0xAA, VALID_MLKEM_KEY, 100, 200);
        uint256 gasUsed = gasBefore - gasleft();

        emit log_named_uint("ML-KEM-768 Account Registration Live Fork Gas", gasUsed);
        (, , , , , bool isRegistered) = registry.accounts(1);
        assertTrue(isRegistered);
        assertEq(registry.getViewKey(1).length, 1184);
    }

    /// @notice Test 3: Measure live gas of recording pairwise post-quantum key agreement on Mainnet fork
    function test_MainnetFork_PairwiseAgreement_LiveGas() public {
        registry.registerAccount(1, bank1, 0x11, VALID_MLKEM_KEY, 10, 20);
        registry.registerAccount(2, bank2, 0x22, VALID_MLKEM_KEY, 30, 40);

        uint256 gasBefore = gasleft();
        registry.recordPairwiseAgreement(1, 2, VALID_MLKEM_CIPHERTEXT, CONFIRMATION_TAG, CONFIRMATION_TAG);
        uint256 gasUsed = gasBefore - gasleft();

        emit log_named_uint("ML-KEM-768 Pairwise Agreement Live Fork Gas", gasUsed);
        assertTrue(registry.getPairwiseAgreement(1, 2).isEstablished);
    }
}
