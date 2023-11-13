// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.15;

contract LibTest {

    enum ItemType {
    // 0: ETH on mainnet, MATIC on polygon, etc.
        NATIVE,

        // 1: ERC20 items (ERC777 and ERC20 analogues could also technically work)
        ERC20,

        // 2: ERC721 items
        ERC721,

        // 3: ERC1155 items
        ERC1155,

        // 4: ERC721 items where a number of tokenIds are supported
        ERC721_WITH_CRITERIA,

        // 5: ERC1155 items where a number of ids are supported
        ERC1155_WITH_CRITERIA
    }

    struct ReceivedItem {
        ItemType itemType;
        address token;
        uint256 identifier;
        uint256 amount;
        address payable recipient;
    }

    struct Execution {
        ReceivedItem item;
        address offerer;
        bytes32 conduitKey;
    }

    function _executeAvailableFulfillments(
        uint256[][] memory offerFulfillments,
        uint256[][] memory considerationFulfillments,
        bytes32 fulfillerConduitKey,
        address recipient
    )
        internal
        returns (bool[] memory availableOrders, Execution[] memory executions)
    {
        // Retrieve length of offer fulfillments array and place on the stack.
        uint256 totalOfferFulfillments = offerFulfillments.length;

        // Retrieve length of consideration fulfillments array & place on stack.
        uint256 totalConsiderationFulfillments = (
            considerationFulfillments.length
        );

        executions = new Execution[](
            totalOfferFulfillments + totalConsiderationFulfillments
        );

        // Track number of filtered executions.
        uint256 totalFilteredExecutions = 0;

        // Iterate over each offer fulfillment.
        for (uint256 i = 0; i < totalOfferFulfillments; ++i) {

            // Derive aggregated execution corresponding with fulfillment.
            Execution memory execution = executions[i];

            // If offerer and recipient on the execution are the same...
            if (execution.item.recipient == execution.offerer) {
                // increment total filtered executions.
                totalFilteredExecutions += 1;
            } else {
                // Otherwise, assign the execution to the executions array.
                executions[i - totalFilteredExecutions] = execution;
                 }
        }

        // Iterate over each consideration fulfillment.
        for (uint256 i = 0; i < totalConsiderationFulfillments; ++i) {
            Execution memory execution = executions[i];

            // If offerer and recipient on the execution are the same...
            if (execution.item.recipient == execution.offerer) {
                // increment total filtered executions.
                totalFilteredExecutions += 1;
            } else {
                // Otherwise, assign the execution to the executions array.
                executions[
                    i + totalOfferFulfillments - totalFilteredExecutions
                ] = execution;
            }
        }

        // If some number of executions have been filtered...
        if (totalFilteredExecutions != 0) {
            /**
             *   The following is highly inefficient, but written this way
             *   to show in the most simplest form what the optimized
             *   contract is performing inside its assembly.
             */

            // Get the total execution length.
            uint256 executionLength = (totalOfferFulfillments +
                totalConsiderationFulfillments) - totalFilteredExecutions;

            // Create an array of executions that will be executed.
            Execution[] memory filteredExecutions = new Execution[](
                executionLength
            );

            // Create new array from the existing Executions
            for (uint256 i = 0; i < executionLength; ++i) {
                filteredExecutions[i] = executions[i];
            }

            // Set the executions array to the newly created array.
            executions = filteredExecutions;
        }

        return (availableOrders, executions);
    }
}

contract LibTest2 {
    function fpow(
        uint256 x,
        uint256 n,
        uint256 decimals
    ) internal pure returns (uint256 z) {
        uint256 b = 10**decimals;
        assembly {
            switch x
            case 0 {
                switch n
                case 0 {
                    z := b
                }
                default {
                    z := 0
                }
            }
            default {
                switch mod(n, 2)
                case 0 {
                    z := b
                }
                default {
                    z := x
                }
                let half := div(b, 2)
                for {
                    n := div(n, 2)
                } n {
                    n := div(n, 2)
                } {
                    let xx := mul(x, x)
                    if iszero(eq(div(xx, x), x)) {
                        revert(0, 0)
                    }
                    let xxRound := add(xx, half)
                    if lt(xxRound, xx) {
                        revert(0, 0)
                    }
                    x := div(xxRound, b)
                    if mod(n, 2) {
                        let zx := mul(z, x)
                        if and(iszero(iszero(x)), iszero(eq(div(zx, x), z))) {
                            revert(0, 0)
                             }
                        let zxRound := add(zx, half)
                        if lt(zxRound, zx) {
                            revert(0, 0)
                        }
                        z := div(zxRound, b)
                    }
                }
            }
        }
    }
}

contract LibTest3 {
    uint totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    function approve(address spender, uint256 value) external returns (bool) {
        allowance[msg.sender][spender] = value;

        return true;
    }

    function transfer(address to, uint256 value) external returns (bool) {
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;  

        return true;
    }


    function transferFrom(
        address from,
        address to,
        uint256 value
    ) external returns (bool) {
        if (allowance[from][msg.sender] != type(uint256).max) {
            allowance[from][msg.sender] -= value;
        }

        balanceOf[from] -= value;
        balanceOf[to] += value;    

        return true;
    }


    function _mint(address to, uint256 value) internal {
        totalSupply += value;   
        balanceOf[to] += value; 
    }


    function _burn(address from, uint256 value) internal {
        balanceOf[from] -= value;  // line 1
        totalSupply -= value;      // line 2
    }

}