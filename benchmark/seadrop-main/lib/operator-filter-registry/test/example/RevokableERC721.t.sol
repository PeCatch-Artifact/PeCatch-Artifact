// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {RevokableExampleERC721} from "../../src/example/RevokableExampleERC721.sol";
import {BaseRegistryTest} from "../BaseRegistryTest.sol";
import {IERC165} from "openzeppelin-contracts/interfaces/IERC165.sol";
import {IERC721} from "openzeppelin-contracts/interfaces/IERC721.sol";
import {IERC2981} from "openzeppelin-contracts/interfaces/IERC2981.sol";

contract TestableExampleERC721 is RevokableExampleERC721 {
    function mint(address to, uint256 tokenId) external {
        _mint(to, tokenId);
    }
}

contract RevokableExampleERC721Test is BaseRegistryTest {
    TestableExampleERC721 example;
    address filteredAddress;

    address constant DEFAULT_SUBSCRIPTION = address(0x3cc6CddA760b79bAfa08dF41ECFA224f810dCeB6);

    function setUp() public override {
        super.setUp();

        vm.startPrank(DEFAULT_SUBSCRIPTION);
        registry.register(DEFAULT_SUBSCRIPTION);

        filteredAddress = makeAddr("filtered address");
        registry.updateOperator(address(DEFAULT_SUBSCRIPTION), filteredAddress, true);
        vm.stopPrank();

        example = new TestableExampleERC721();
    }

    function testFilter() public {
        vm.startPrank(address(filteredAddress));
        vm.expectRevert(abi.encodeWithSelector(AddressFiltered.selector, filteredAddress));
        example.transferFrom(makeAddr("from"), makeAddr("to"), 1);
        vm.expectRevert(abi.encodeWithSelector(AddressFiltered.selector, filteredAddress));
        example.safeTransferFrom(makeAddr("from"), makeAddr("to"), 1);
        vm.expectRevert(abi.encodeWithSelector(AddressFiltered.selector, filteredAddress));
        example.safeTransferFrom(makeAddr("from"), makeAddr("to"), 1, "");
    }

    function testOwnersNotExcluded() public {
        address alice = address(0xA11CE);
        example.mint(alice, 1);

        vm.prank(DEFAULT_SUBSCRIPTION);
        registry.updateOperator(address(DEFAULT_SUBSCRIPTION), alice, true);

        vm.prank(alice);
        example.transferFrom(alice, makeAddr("to"), 1);
    }

    function testOwnersNotExcludedSafeTransfer() public {
        address alice = address(0xA11CE);
        example.mint(alice, 1);
        example.mint(alice, 2);

        vm.prank(DEFAULT_SUBSCRIPTION);
        registry.updateOperator(address(DEFAULT_SUBSCRIPTION), alice, true);

        vm.startPrank(alice);
        example.safeTransferFrom(alice, makeAddr("to"), 1);
        example.safeTransferFrom(alice, makeAddr("to"), 2, "");
    }

    function testExclusionExceptionDoesNotApplyToOperators() public {
        address alice = address(0xA11CE);
        address bob = address(0xB0B);
        example.mint(bob, 1);
        vm.prank(bob);
        example.setApprovalForAll(alice, true);

        vm.prank(DEFAULT_SUBSCRIPTION);
        registry.updateOperator(address(DEFAULT_SUBSCRIPTION), alice, true);

        vm.startPrank(alice);
        vm.expectRevert(abi.encodeWithSelector(AddressFiltered.selector, alice));
        example.transferFrom(bob, makeAddr("to"), 1);
    }

    function testExcludeApprovals() public {
        address alice = address(0xA11CE);
        address bob = address(0xB0B);
        example.mint(bob, 1);

        vm.prank(DEFAULT_SUBSCRIPTION);
        registry.updateOperator(address(DEFAULT_SUBSCRIPTION), alice, true);

        vm.startPrank(bob);
        vm.expectRevert(abi.encodeWithSelector(AddressFiltered.selector, alice));
        example.setApprovalForAll(alice, true);

        vm.expectRevert(abi.encodeWithSelector(AddressFiltered.selector, alice));
        example.approve(alice, 1);
    }

    function testRevoke() public {
        address alice = makeAddr("alice");
        address bob = makeAddr("bob");
        example.mint(makeAddr("bob"), 1);

        vm.prank(DEFAULT_SUBSCRIPTION);
        registry.updateOperator(address(DEFAULT_SUBSCRIPTION), alice, true);

        example.updateOperatorFilterRegistryAddress(address(0));

        vm.prank(bob);
        example.setApprovalForAll(alice, true);
        vm.startPrank(alice);
        example.safeTransferFrom(bob, makeAddr("to"), 1);
    }

    function testSupportsInterface() public {
        assertTrue(example.supportsInterface(type(IERC165).interfaceId));
        assertTrue(example.supportsInterface(type(IERC721).interfaceId));
        assertTrue(example.supportsInterface(type(IERC2981).interfaceId));
    }
}
