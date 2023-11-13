/* Autogenerated file. Do not edit manually. */
/* tslint:disable */
/* eslint-disable */

import {
  ethers,
  EventFilter,
  Signer,
  BigNumber,
  BigNumberish,
  PopulatedTransaction,
} from "ethers";
import {
  Contract,
  ContractTransaction,
  PayableOverrides,
  CallOverrides,
} from "@ethersproject/contracts";
import { BytesLike } from "@ethersproject/bytes";
import { Listener, Provider } from "@ethersproject/providers";
import { FunctionFragment, EventFragment, Result } from "@ethersproject/abi";

interface IPoolInitializerInterface extends ethers.utils.Interface {
  functions: {
    "createAndInitializePoolIfNecessary(address,address,uint24,uint160)": FunctionFragment;
  };

  encodeFunctionData(
    functionFragment: "createAndInitializePoolIfNecessary",
    values: [string, string, BigNumberish, BigNumberish]
  ): string;

  decodeFunctionResult(
    functionFragment: "createAndInitializePoolIfNecessary",
    data: BytesLike
  ): Result;

  events: {};
}

export class IPoolInitializer extends Contract {
  connect(signerOrProvider: Signer | Provider | string): this;
  attach(addressOrName: string): this;
  deployed(): Promise<this>;

  on(event: EventFilter | string, listener: Listener): this;
  once(event: EventFilter | string, listener: Listener): this;
  addListener(eventName: EventFilter | string, listener: Listener): this;
  removeAllListeners(eventName: EventFilter | string): this;
  removeListener(eventName: any, listener: Listener): this;

  interface: IPoolInitializerInterface;

  functions: {
    createAndInitializePoolIfNecessary(
      token0: string,
      token1: string,
      fee: BigNumberish,
      sqrtPriceX96: BigNumberish,
      overrides?: PayableOverrides
    ): Promise<ContractTransaction>;

    "createAndInitializePoolIfNecessary(address,address,uint24,uint160)"(
      token0: string,
      token1: string,
      fee: BigNumberish,
      sqrtPriceX96: BigNumberish,
      overrides?: PayableOverrides
    ): Promise<ContractTransaction>;
  };

  createAndInitializePoolIfNecessary(
    token0: string,
    token1: string,
    fee: BigNumberish,
    sqrtPriceX96: BigNumberish,
    overrides?: PayableOverrides
  ): Promise<ContractTransaction>;

  "createAndInitializePoolIfNecessary(address,address,uint24,uint160)"(
    token0: string,
    token1: string,
    fee: BigNumberish,
    sqrtPriceX96: BigNumberish,
    overrides?: PayableOverrides
  ): Promise<ContractTransaction>;

  callStatic: {
    createAndInitializePoolIfNecessary(
      token0: string,
      token1: string,
      fee: BigNumberish,
      sqrtPriceX96: BigNumberish,
      overrides?: CallOverrides
    ): Promise<string>;

    "createAndInitializePoolIfNecessary(address,address,uint24,uint160)"(
      token0: string,
      token1: string,
      fee: BigNumberish,
      sqrtPriceX96: BigNumberish,
      overrides?: CallOverrides
    ): Promise<string>;
  };

  filters: {};

  estimateGas: {
    createAndInitializePoolIfNecessary(
      token0: string,
      token1: string,
      fee: BigNumberish,
      sqrtPriceX96: BigNumberish,
      overrides?: PayableOverrides
    ): Promise<BigNumber>;

    "createAndInitializePoolIfNecessary(address,address,uint24,uint160)"(
      token0: string,
      token1: string,
      fee: BigNumberish,
      sqrtPriceX96: BigNumberish,
      overrides?: PayableOverrides
    ): Promise<BigNumber>;
  };

  populateTransaction: {
    createAndInitializePoolIfNecessary(
      token0: string,
      token1: string,
      fee: BigNumberish,
      sqrtPriceX96: BigNumberish,
      overrides?: PayableOverrides
    ): Promise<PopulatedTransaction>;

    "createAndInitializePoolIfNecessary(address,address,uint24,uint160)"(
      token0: string,
      token1: string,
      fee: BigNumberish,
      sqrtPriceX96: BigNumberish,
      overrides?: PayableOverrides
    ): Promise<PopulatedTransaction>;
  };
}
