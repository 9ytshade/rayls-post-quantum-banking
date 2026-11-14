// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "forge-std/Test.sol";
import "../contracts/PQAccountRegistry.sol";

contract PQInvariantAuditTest is Test {
    PQAccountRegistry public registry;
    address public bank1 = address(0x1111);
    address public bank2 = address(0x2222);
    address public attacker = address(0x9999);

    bytes constant VALID_MLKEM_KEY = new bytes(1184);
    bytes constant VALID_MLKEM_CIPHERTEXT = new bytes(1088);
    bytes constant TRUNCATED_X25519_KEY = new bytes(32);
    bytes constant TRUNCATED_CIPHERTEXT = new bytes(32);

    bytes32 constant EXPECTED_CONFIRMATION_TAG = keccak256("enygma-view-key-confirm-v1:rawSharedSecret");
    bytes32 constant CORRUPTED_CONFIRMATION_TAG = keccak256("fips203-implicit-rejection-pseudorandom-key");

    function setUp() public {
        PQAccountRegistry.GuardConfig memory initialGuards = PQAccountRegistry.GuardConfig({
            enforceKeyLength: true,
            enforceCiphertextLength: true,
            enforceLeaderOrdering: true,
            enforceConfirmationTag: true
        });
        registry = new PQAccountRegistry(initialGuards);
    }

    /// @notice Test 1: Happy path registration of a full 1,184-byte ML-KEM-768 view key
    function test_HappyPath_RegisterMLKEM768Account() public {
        vm.prank(bank1);
        registry.registerAccount(1, bank1, 0xAA, VALID_MLKEM_KEY, 100, 200);

        (address addr, uint256 pubKey, bytes memory vk, uint256 cX, uint256 cY, bool reg) = registry.accounts(1);
        assertTrue(reg);
        assertEq(addr, bank1);
        assertEq(pubKey, 0xAA);
        assertEq(vk.length, 1184);
        assertEq(cX, 100);
        assertEq(cY, 200);
    }

    /// @notice Test 2: Relayer registration with legitimately empty view key (0 bytes)
    function test_HappyPath_RelayerEmptyViewKey() public {
        bytes memory emptyKey = new bytes(0);
        registry.registerAccount(1, bank1, 0xBB, emptyKey, 50, 60);

        bytes memory vk = registry.getViewKey(1);
        assertEq(vk.length, 0);
    }

    /// @notice Test 3: CRIT-PQ1 - Guard OFF allows registering truncated classical key; Guard ON rejects it
    function test_Counterfactual_CRIT_PQ1_GuardOffAllowsTruncatedClassicalKey_GuardOnReverts() public {
        // Step A: Guard OFF permits classical 32-byte X25519 key (Vulnerable state)
        registry.setGuards(PQAccountRegistry.GuardConfig(false, true, true, true));
        registry.registerAccount(1, bank1, 0x11, TRUNCATED_X25519_KEY, 10, 20);
        assertEq(registry.getViewKey(1).length, 32);

        // Deploy fresh contract with Guard ON
        registry = new PQAccountRegistry(PQAccountRegistry.GuardConfig(true, true, true, true));

        // Step B: Guard ON strictly enforces 1184-byte ML-KEM-768 key
        vm.expectRevert(PQAccountRegistry.InvalidViewKeyLength.selector);
        registry.registerAccount(1, bank1, 0x11, TRUNCATED_X25519_KEY, 10, 20);
    }

    /// @notice Test 4: CRIT-PQ2 - Guard OFF allows FIPS 203 implicit rejection desync; Guard ON enforces confirmation tag
    function test_Counterfactual_CRIT_PQ2_GuardOffAllowsCorruptedCiphertext_GuardOnReverts() public {
        registry.registerAccount(1, bank1, 0x11, VALID_MLKEM_KEY, 10, 20);
        registry.registerAccount(2, bank2, 0x22, VALID_MLKEM_KEY, 30, 40);

        // Step A: Guard OFF allows mismatched confirmation tag (simulating corrupted ciphertext)
        registry.setGuards(PQAccountRegistry.GuardConfig(true, true, true, false));
        registry.recordPairwiseAgreement(1, 2, VALID_MLKEM_CIPHERTEXT, CORRUPTED_CONFIRMATION_TAG, EXPECTED_CONFIRMATION_TAG);
        assertTrue(registry.getPairwiseAgreement(1, 2).isEstablished);

        // Reset and test Guard ON
        registry = new PQAccountRegistry(PQAccountRegistry.GuardConfig(true, true, true, true));
        registry.registerAccount(1, bank1, 0x11, VALID_MLKEM_KEY, 10, 20);
        registry.registerAccount(2, bank2, 0x22, VALID_MLKEM_KEY, 30, 40);

        // Step B: Guard ON rejects corrupted ciphertext confirmation
        vm.expectRevert(PQAccountRegistry.CorruptedCiphertextRejected.selector);
        registry.recordPairwiseAgreement(1, 2, VALID_MLKEM_CIPHERTEXT, CORRUPTED_CONFIRMATION_TAG, EXPECTED_CONFIRMATION_TAG);
    }

    /// @notice Test 5: CRIT-PQ3 - Fix M-11 defect 1: Leader must have lower ID than follower
    function test_Counterfactual_CRIT_PQ3_GuardOffAllowsLeaderRace_GuardOnEnforcesLowerId() public {
        registry.registerAccount(1, bank1, 0x11, VALID_MLKEM_KEY, 10, 20);
        registry.registerAccount(2, bank2, 0x22, VALID_MLKEM_KEY, 30, 40);

        // Step A: Bank 2 improperly leads key agreement with Bank 1 under Guard OFF
        registry.setGuards(PQAccountRegistry.GuardConfig(true, true, false, true));
        registry.recordPairwiseAgreement(2, 1, VALID_MLKEM_CIPHERTEXT, EXPECTED_CONFIRMATION_TAG, EXPECTED_CONFIRMATION_TAG);
        assertTrue(registry.getPairwiseAgreement(2, 1).isEstablished);

        // Reset and test Guard ON
        registry = new PQAccountRegistry(PQAccountRegistry.GuardConfig(true, true, true, true));
        registry.registerAccount(1, bank1, 0x11, VALID_MLKEM_KEY, 10, 20);
        registry.registerAccount(2, bank2, 0x22, VALID_MLKEM_KEY, 30, 40);

        // Step B: Guard ON blocks higher bank ID from leading
        vm.expectRevert(PQAccountRegistry.UnauthorizedLeaderDirection.selector);
        registry.recordPairwiseAgreement(2, 1, VALID_MLKEM_CIPHERTEXT, EXPECTED_CONFIRMATION_TAG, EXPECTED_CONFIRMATION_TAG);
    }

    /// @notice Test 6: CRIT-PQ4 - Ciphertext length must be exactly 1,088 bytes
    function test_Counterfactual_CRIT_PQ4_GuardOffAllowsTruncatedCiphertext_GuardOnReverts() public {
        registry.registerAccount(1, bank1, 0x11, VALID_MLKEM_KEY, 10, 20);
        registry.registerAccount(2, bank2, 0x22, VALID_MLKEM_KEY, 30, 40);

        // Step A: Guard OFF allows truncated 32-byte ciphertext
        registry.setGuards(PQAccountRegistry.GuardConfig(true, false, true, true));
        registry.recordPairwiseAgreement(1, 2, TRUNCATED_CIPHERTEXT, EXPECTED_CONFIRMATION_TAG, EXPECTED_CONFIRMATION_TAG);
        assertTrue(registry.getPairwiseAgreement(1, 2).isEstablished);

        // Reset and test Guard ON
        registry = new PQAccountRegistry(PQAccountRegistry.GuardConfig(true, true, true, true));
        registry.registerAccount(1, bank1, 0x11, VALID_MLKEM_KEY, 10, 20);
        registry.registerAccount(2, bank2, 0x22, VALID_MLKEM_KEY, 30, 40);

        // Step B: Guard ON rejects truncated ciphertext
        vm.expectRevert(PQAccountRegistry.InvalidCiphertextLength.selector);
        registry.recordPairwiseAgreement(1, 2, TRUNCATED_CIPHERTEXT, EXPECTED_CONFIRMATION_TAG, EXPECTED_CONFIRMATION_TAG);
    }

    /// @notice Test 7: Non-sequential account ID assignment is rejected
    function test_SequentialAccountIdEnforcement() public {
        registry.registerAccount(1, bank1, 0x11, VALID_MLKEM_KEY, 10, 20);

        // Skip account 2 and try registering account 3
        vm.expectRevert(PQAccountRegistry.InvalidAccountId.selector);
        registry.registerAccount(3, bank2, 0x22, VALID_MLKEM_KEY, 30, 40);
    }

    /// @notice Test 8: Fuzzing arbitrary view-key lengths
    function testFuzz_ArbitraryMalformedKeyLengthsRevert(uint16 keyLength) public {
        vm.assume(keyLength != 0 && keyLength != 1184);
        bytes memory malformedKey = new bytes(keyLength);

        vm.expectRevert(PQAccountRegistry.InvalidViewKeyLength.selector);
        registry.registerAccount(1, bank1, 0x11, malformedKey, 10, 20);
    }
}
