// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.5.0;
// pragma abicoder v2;

import "./libraries/SafeMath.sol";
import "./libraries/Oracle.sol";

contract LibTest1 {
    mapping (uint256 => mapping(address => uint256)) private _balances;

     function safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    )
        public
    {
        require(_balances[id][from] >= amount, "ERC1155: insufficient balance for transfer");
        _balances[id][from] -= amount;
        _balances[id][to] += amount;
    }

    function safeBatchTransferFrom(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    )
        public
    {
        for (uint256 i = 0; i < ids.length; ++i) {
            uint256 id = ids[i];
            uint256 amount = amounts[i];

            require(_balances[id][from] >= amount, "ERC1155: insufficient balance for transfer");
            _balances[id][from] -= amount;
            _balances[id][to] += amount;
        }
    }

    function _burn(address account, uint256 id, uint256 amount) internal {
        require(account != address(0), "ERC1155: burn from the zero address");

        require(_balances[id][account] >= amount, "ERC1155: burn amount exceeds balance");
        _balances[id][account] -= amount;
    }

    function _burnBatch(address account, uint256[] memory ids, uint256[] memory amounts) internal {
        require(account != address(0), "ERC1155: burn from the zero address");
        require(ids.length == amounts.length, "ERC1155: ids and amounts length mismatch");

        for (uint i = 0; i < ids.length; i++) {
            uint256 id = ids[i];
            uint256 amount = amounts[i];

            require(_balances[id][account] >= amount, "ERC1155: burn amount exceeds balance");
            _balances[id][account] -= amount;
        }
    }
}

contract LibTest2 {

    uint _totalSupply;
    mapping(address => uint256) public _balances;
    mapping (address => mapping (address => uint256)) private _allowances;

    function _msgSender() internal view returns (address) {
        return msg.sender;
    }

    function transferFrom(address sender, address recipient, uint256 amount) public returns (bool) {
        _transfer(sender, recipient, amount);

        require(_allowances[sender][_msgSender()] >= amount, "ERC20: transfer amount exceeds allowance");
        _approve(sender, _msgSender(), _allowances[sender][_msgSender()] - amount);

        return true;
    }

    function decreaseAllowance(address spender, uint256 subtractedValue) public returns (bool) {
        require(_allowances[_msgSender()][spender] >= subtractedValue, "ERC20: decreased allowance below zero");
        _approve(_msgSender(), spender, _allowances[_msgSender()][spender] - subtractedValue);

        return true;
    }

    function _transfer(address sender, address recipient, uint256 amount) internal {
        require(sender != address(0), "ERC20: transfer from the zero address");
        require(recipient != address(0), "ERC20: transfer to the zero address");

        require(_balances[sender] >= amount, "ERC20: transfer amount exceeds balance");
        _balances[sender] -= amount;

        _balances[recipient] += amount;
    }

    function _burn(address account, uint256 amount) internal {
        require(account != address(0), "ERC20: burn from the zero address");

        require(_balances[account] >= amount, "ERC20: burn amount exceeds balance");
        _balances[account] -= amount;
    }

    function _approve(address owner, address spender, uint256 amount) internal {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");
        _allowances[owner][spender] = amount;
    }

    function transferFrom2(address holder, address recipient, uint256 amount) public returns (bool) {
        require(recipient != address(0), "ERC777: transfer to the zero address");
        require(holder != address(0), "ERC777: transfer from the zero address");

        address spender = _msgSender();

        require(_allowances[holder][spender] >= amount, "ERC777: transfer amount exceeds allowance");
        _approve(holder, spender, _allowances[holder][spender] - amount);

        return true;
    }

    function _burn(
        address from,
        uint256 amount,
        bytes memory data,
        bytes memory operatorData
    )
        internal
    {
        require(from != address(0), "ERC777: burn from the zero address");

        // Update state variables
        require(_balances[from] >= amount, "ERC777: burn amount exceeds balance");
        _balances[from] -= amount;

        _totalSupply -= amount;
    }

    function _move(
        address operator,
        address from,
        address to,
        uint256 amount,
        bytes memory userData,
        bytes memory operatorData
    )
        private
    {

        require(_balances[from] >= amount, "ERC777: transfer amount exceeds balance");
        _balances[from] -= amount;
        _balances[to] += amount;
    }

    function allowance(address owner, address spender) public view returns (uint256) {
        return _allowances[owner][spender];
    }

    function burnFrom(address account, uint256 amount) public {
        require(allowance(account, _msgSender()) >= amount, "ERC20: burn amount exceeds allowance");
        _approve(account, _msgSender(), allowance(account, _msgSender()) - amount);
    }
}

contract LibTest3 {

    struct ConduitProperties{
        address owner;
        bytes32 key;
    }

    struct OrderStatus{
        bool isValidated;
        bool isCancelled;
        uint128 numerator;
        uint128 denominator;
    }

    mapping(address => ConduitProperties) internal _conduits;
    mapping(bytes32 => OrderStatus) private _orderStatus;

     function createConduit(bytes32 conduitKey, address initialOwner)
        external
        returns (address conduit)
    {

        // Set the supplied initial owner as the owner of the conduit.
        _conduits[conduit].owner = initialOwner;

        // Set conduit key used to deploy the conduit to enable reverse lookup.
        _conduits[conduit].key = conduitKey;
    }

    function _validateBasicOrderAndUpdateStatus(
        bytes32 orderHash,
        address offerer,
        bytes memory signature,
        OrderStatus memory orderStatus
    ) internal {

        // Update order status as fully filled, packing struct values.
        _orderStatus[orderHash].isValidated = true;
        _orderStatus[orderHash].isCancelled = false;
        _orderStatus[orderHash].numerator = 1;
        _orderStatus[orderHash].denominator = 1;

        // If the order is not entirely unused...
        if (orderStatus.numerator != 0) {
            // ensure the order has not been partially filled when not allowed.
            if (orderStatus.numerator >= orderStatus.denominator) {
            }
        }
    }
}

contract LibTest4 {

    struct OrderParam{
        address offerer;
        address zone;
    }

    struct Order{
        OrderParam param;
        address offerer;
        address zone;
    }

    Order order;

    event OrderCancelled(address offerer, address zone);

    function cancel(
        uint256[] memory orders
    ) public returns (bool) {

        // Skip overflow check as for loop is indexed starting at zero.
        // unchecked {
            // Iterate over each order.
            for (uint256 i = 0; i < orders.length; ++i) {
                // Retrieve the order.

                // Ensure caller is either offerer or zone of the order.
                if (
                    msg.sender != order.offerer &&
                    msg.sender != order.zone
                ) {
                }
            // }
            emit OrderCancelled(
                order.offerer,
                order.zone

            );

            bytes32 orderHash = _getNoncedOrderHash(order.param);

            _getOrderStatusAndVerify(
                    orderHash,
                    order.param.offerer
                );

            emit OrderCancelled(
                order.param.offerer,
                order.param.zone
            );

        }
    }

    function _getNoncedOrderHash(OrderParam memory param) internal returns (bytes32 a) {
        a = 0x00; 
    }

    function _getOrderStatusAndVerify(bytes32 orderHash, address offerer) internal {
    }
}

contract LibTest5 {
    
    struct Info {
        uint a;
    }

    uint8 public constant NUM_FEE_OPTIONS = 6;
    uint112[NUM_FEE_OPTIONS] public virtualSupplies;


    function test(Info storage info) internal {
        uint b = info.a;
        uint c = info.a;
    }

    function test2() public {

    }
}

contract LibTest6 {
    struct Slot0 {
        // the last block timestamp where the tick accumulator was updated
        uint32 blockTimestampLast;
        // the tick accumulator, i.e. tick * time elapsed since the pair was first initialized
        int56 tickCumulativeLast;
        // whether the pair is locked for swapping, and whether the price is below the current tick boundary
        uint8 unlockedAndPriceBit;
    }
    struct Info {
        // the total position liquidity that references this tick
        uint128 liquidityGross;
        // amount of net liquidity added (subtracted) when tick is crossed from left to right (right to left),
        int128 liquidityNet;
        // fee growth per unit of liquidity on the _other_ side of this tick (relative to the current tick)
        // only has relative meaning, not absolute — the value depends on when the tick is initialized
        uint256 feeGrowthOutside0X128;
        uint256 feeGrowthOutside1X128;
        // the cumulative tick value on the other side of the tick
        int56 tickCumulativeOutside;
        // the seconds per unit of liquidity on the _other_ side of this tick (relative to the current tick)
        // only has relative meaning, not absolute — the value depends on when the tick is initialized
        uint160 secondsPerLiquidityOutsideX128;
        // the seconds spent on the other side of the tick (relative to the current tick)
        // only has relative meaning, not absolute — the value depends on when the tick is initialized
        uint32 secondsOutside;
        // true iff the tick is initialized, i.e. the value is exactly equivalent to the expression liquidityGross != 0
        // these 8 bits are set to prevent fresh sstores when crossing newly initialized ticks
        bool initialized;
    }
    Slot0 public slot0;
    mapping(uint24 => int24) public feeAmountTickSpacing;
    mapping(int24 => Info) public ticks;
    mapping(address => mapping(uint256 => uint256)) public balanceOf;

    modifier lock() {
        require(slot0.unlockedAndPriceBit >= 1, 'UniswapV3Pair::lock: reentrancy prohibited');
        slot0.unlockedAndPriceBit ^= 1;
        _;
        slot0.unlockedAndPriceBit ^= 1;

    }

    function enableFeeAmount(uint24 fee, int24 tickSpacing) public {
        require(fee < 1000000);
        // tick spacing is capped at 16384 to prevent the situation where tickSpacing is so large that
        // TickBitmap#nextInitializedTickWithinOneWord overflows int24 container from a valid tick
        // 16384 ticks represents a >5x price change with ticks of 1 bips
        require(tickSpacing > 0 && tickSpacing < 16384);
        require(feeAmountTickSpacing[fee] == 0);

        feeAmountTickSpacing[fee] = tickSpacing;
    }

    function snapshotCumulativesInside(int24 tickLower, int24 tickUpper)
        external
        returns (
            int56 tickCumulativeInside,
            uint160 secondsPerLiquidityInsideX128,
            uint32 secondsInside
        )
    {

        int56 tickCumulativeLower;
        int56 tickCumulativeUpper;
        uint160 secondsPerLiquidityOutsideLowerX128;
        uint160 secondsPerLiquidityOutsideUpperX128;
        uint32 secondsOutsideLower;
        uint32 secondsOutsideUpper;

        {
            Info storage lower = ticks[tickLower];
            Info storage upper = ticks[tickUpper];
            bool initializedLower;
            (tickCumulativeLower, secondsPerLiquidityOutsideLowerX128, secondsOutsideLower, initializedLower) = (
                lower.tickCumulativeOutside,
                lower.secondsPerLiquidityOutsideX128,
                lower.secondsOutside,
                lower.initialized
            );
            require(initializedLower);

            bool initializedUpper;
            (tickCumulativeUpper, secondsPerLiquidityOutsideUpperX128, secondsOutsideUpper, initializedUpper) = (
                upper.tickCumulativeOutside,
                upper.secondsPerLiquidityOutsideX128,
                upper.secondsOutside,
                upper.initialized
            );
            require(initializedUpper);
        }
    }

    function balanceOfBatch(address[] calldata owners, uint256[] calldata ids)
       public
       view
       returns (uint256[] memory balances)
   {
       uint256 len = owners.length;
       require(len == ids.length, "LENGTH_MISMATCH");

       balances = new uint256[](len);

       // Unchecked because the only math done is incrementing
       // the array index counter which cannot possibly overflow.
    //    unchecked {
           for (uint256 i = 0; i < len; ++i) {
               balances[i] = balanceOf[owners[i]][ids[i]];
           }
    //    }
   }

}

contract LibTest7 {

    event ObservationCardinalityNextIncreased(uint16 last, uint16 next);

    using Oracle for Oracle.Observation[65535];
    using SafeMath for uint;
    mapping (address => mapping (address => uint)) private _allowances;
    LibTest5 lt;

    struct Slot0 {
        // the current maximum number of observations that are being stored
        uint16 observationCardinality;
        // the next maximum number of observations to store, triggered in observations.write
        uint16 observationCardinalityNext;
    }
    Slot0 public slot0;
    Oracle.Observation[65535] public observations;

    function transferFrom3(address from, address to, uint value) external returns (bool) {
        if (_allowances[from][msg.sender] > 0) {
            _allowances[from][msg.sender] = _allowances[from][msg.sender].sub(value);
        }
        lt.test2();
        return true;
    }

    function increaseObservationCardinalityNext(uint16 observationCardinalityNext) external {
        require(slot0.observationCardinality > 0, 'I');
        uint16 last = slot0.observationCardinalityNext; // for the event
        slot0.observationCardinalityNext = observations.grow(
            slot0.observationCardinalityNext,
            observationCardinalityNext
        );

        emit ObservationCardinalityNextIncreased(last, slot0.observationCardinalityNext);
    }

}
