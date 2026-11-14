// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @title PQAccountRegistry - Architectural Prototype & Illustrative Invariant Testbench
/// @author 9ytshade
/// @notice Note on Test Scope: This contract evaluates an illustrative reference implementation
///         constructed to model the documented post-quantum invariants of Enygma.sol (viewKey length)
///         and agreement/manager.go (Fix M-11 pairwise agreement & FIPS 203 implicit rejection mitigation).
///         It demonstrates key validation, mutual confirmation tags, and state-machine transitions
///         in an EVM runtime, but does not constitute an audit of Rayls' closed-source or enterprise nodes.
contract PQAccountRegistry {
    // NIST FIPS 203 ML-KEM-768 parameters
    uint256 public constant MLKEM768_PUBLIC_KEY_BYTES = 1184;
    uint256 public constant MLKEM768_CIPHERTEXT_BYTES = 1088;
    uint256 public constant SHARED_SECRET_BYTES = 32;

    struct AccountRecord {
        address accountAddress;
        uint256 publicKey;
        bytes viewKey; // ML-KEM-768 encapsulation key (1184 bytes)
        uint256 initialCommitX;
        uint256 initialCommitY;
        bool isRegistered;
    }

    struct PairwiseAgreementRecord {
        uint256 leaderId;
        uint256 followerId;
        bytes ciphertext; // ML-KEM-768 ciphertext (1088 bytes)
        bytes32 confirmationTag; // SHA-256("enygma-view-key-confirm-v1:" || rawSS)
        uint256 timestamp;
        bool isEstablished;
    }

    struct GuardConfig {
        bool enforceKeyLength;          // Strict 1184-byte view-key enforcement (Enygma.sol line 529)
        bool enforceCiphertextLength;   // Strict 1088-byte ciphertext enforcement
        bool enforceLeaderOrdering;     // Fix M-11 defect 1: lower bankId encapsulates, higher bankId follows
        bool enforceConfirmationTag;    // Fix M-11 defect 2: prevents FIPS 203 implicit rejection desync
    }

    GuardConfig public guards;
    address public immutable owner;
    uint256 public totalRegisteredParties;

    mapping(uint256 => AccountRecord) public accounts;
    mapping(address => uint256) public addressToAccountId;
    mapping(bytes32 => PairwiseAgreementRecord) public pairwiseAgreements;

    event AccountRegistered(uint256 indexed accountId, address indexed accountAddress, uint256 viewKeyLength);
    event PairwiseAgreementEstablished(uint256 indexed leaderId, uint256 indexed followerId, bytes32 confirmationTag);
    event GuardConfigUpdated(bool enforceKeyLength, bool enforceCiphertextLength, bool enforceLeaderOrdering, bool enforceConfirmationTag);

    error AlreadyRegistered();
    error InvalidAccountId();
    error InvalidPublicKey();
    error InvalidViewKeyLength();
    error InvalidCiphertextLength();
    error UnauthorizedLeaderDirection();
    error CorruptedCiphertextRejected();
    error AgreementAlreadyExists();
    error AccountNotRegistered();
    error Unauthorized();

    constructor(GuardConfig memory initialGuards) {
        owner = msg.sender;
        guards = initialGuards;
    }

    function setGuards(GuardConfig memory newGuards) external {
        if (msg.sender != owner) revert Unauthorized();
        guards = newGuards;
        emit GuardConfigUpdated(
            newGuards.enforceKeyLength,
            newGuards.enforceCiphertextLength,
            newGuards.enforceLeaderOrdering,
            newGuards.enforceConfirmationTag
        );
    }

    /// @notice Registers an institutional bank account with its public view key
    /// @dev Implements Enygma.sol's check: viewKey.length == 0 (relayer) or viewKey.length == 1184 (ML-KEM-768)
    function registerAccount(
        uint256 accountId,
        address addr,
        uint256 publicKey,
        bytes calldata viewKey,
        uint256 initialCommitX,
        uint256 initialCommitY
    ) external {
        if (accounts[accountId].isRegistered) revert AlreadyRegistered();
        if (accountId == 0) revert InvalidAccountId();
        if (accountId != totalRegisteredParties + 1) revert InvalidAccountId();
        if (publicKey == 0) revert InvalidPublicKey();

        // Enforce strict ML-KEM-768 encapsulation key length if Guard ON
        if (guards.enforceKeyLength) {
            if (viewKey.length != 0 && viewKey.length != MLKEM768_PUBLIC_KEY_BYTES) {
                revert InvalidViewKeyLength();
            }
        }

        accounts[accountId] = AccountRecord({
            accountAddress: addr,
            publicKey: publicKey,
            viewKey: viewKey,
            initialCommitX: initialCommitX,
            initialCommitY: initialCommitY,
            isRegistered: true
        });

        addressToAccountId[addr] = accountId;
        totalRegisteredParties += 1;

        emit AccountRegistered(accountId, addr, viewKey.length);
    }

    /// @notice Records pairwise post-quantum key agreement between two banks
    /// @dev Implements Fix M-11 leader ordering and mutual confirmation tag verification
    function recordPairwiseAgreement(
        uint256 leaderId,
        uint256 followerId,
        bytes calldata ciphertext,
        bytes32 confirmationTag,
        bytes32 expectedConfirmationTag
    ) external {
        if (!accounts[leaderId].isRegistered || !accounts[followerId].isRegistered) {
            revert AccountNotRegistered();
        }

        // Fix M-11 defect 1: lower bankId must lead
        if (guards.enforceLeaderOrdering) {
            if (!(leaderId < followerId)) {
                revert UnauthorizedLeaderDirection();
            }
        }

        // Enforce strict ML-KEM-768 ciphertext size if Guard ON
        if (guards.enforceCiphertextLength) {
            if (ciphertext.length != MLKEM768_CIPHERTEXT_BYTES) {
                revert InvalidCiphertextLength();
            }
        }

        // Fix M-11 defect 2: FIPS 203 implicit rejection mitigation via confirmation tag
        if (guards.enforceConfirmationTag) {
            if (confirmationTag != expectedConfirmationTag || confirmationTag == bytes32(0)) {
                revert CorruptedCiphertextRejected();
            }
        }

        bytes32 pairKey = keccak256(abi.encodePacked(leaderId, followerId));
        if (pairwiseAgreements[pairKey].isEstablished) {
            revert AgreementAlreadyExists();
        }

        pairwiseAgreements[pairKey] = PairwiseAgreementRecord({
            leaderId: leaderId,
            followerId: followerId,
            ciphertext: ciphertext,
            confirmationTag: confirmationTag,
            timestamp: block.timestamp,
            isEstablished: true
        });

        emit PairwiseAgreementEstablished(leaderId, followerId, confirmationTag);
    }

    function getPairwiseAgreement(uint256 leaderId, uint256 followerId) external view returns (PairwiseAgreementRecord memory) {
        bytes32 pairKey = keccak256(abi.encodePacked(leaderId, followerId));
        return pairwiseAgreements[pairKey];
    }

    function getViewKey(uint256 accountId) external view returns (bytes memory) {
        return accounts[accountId].viewKey;
    }
}
