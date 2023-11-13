/* Autogenerated file. Do not edit manually. */
/* tslint:disable */
/* eslint-disable */
import type {
  BaseContract,
  BigNumber,
  BigNumberish,
  BytesLike,
  CallOverrides,
  ContractTransaction,
  Overrides,
  PopulatedTransaction,
  Signer,
  utils,
} from "ethers";
import type {
  FunctionFragment,
  Result,
  EventFragment,
} from "@ethersproject/abi";
import type { Listener, Provider } from "@ethersproject/providers";
import type {
  TypedEventFilter,
  TypedEvent,
  TypedListener,
  OnEvent,
} from "../../common";

export type ConduitTransferStruct = {
  itemType: BigNumberish;
  token: string;
  from: string;
  to: string;
  identifier: BigNumberish;
  amount: BigNumberish;
};

export type ConduitTransferStructOutput = [
  number,
  string,
  string,
  string,
  BigNumber,
  BigNumber
] & {
  itemType: number;
  token: string;
  from: string;
  to: string;
  identifier: BigNumber;
  amount: BigNumber;
};

export type ConduitBatch1155TransferStruct = {
  token: string;
  from: string;
  to: string;
  ids: BigNumberish[];
  amounts: BigNumberish[];
};

export type ConduitBatch1155TransferStructOutput = [
  string,
  string,
  string,
  BigNumber[],
  BigNumber[]
] & {
  token: string;
  from: string;
  to: string;
  ids: BigNumber[];
  amounts: BigNumber[];
};

export interface ConduitMockInterface extends utils.Interface {
  functions: {
    "execute((uint8,address,address,address,uint256,uint256)[])": FunctionFragment;
    "executeBatch1155((address,address,address,uint256[],uint256[])[])": FunctionFragment;
    "executeWithBatch1155((uint8,address,address,address,uint256,uint256)[],(address,address,address,uint256[],uint256[])[])": FunctionFragment;
    "updateChannel(address,bool)": FunctionFragment;
  };

  getFunction(
    nameOrSignatureOrTopic:
      | "execute"
      | "executeBatch1155"
      | "executeWithBatch1155"
      | "updateChannel"
  ): FunctionFragment;

  encodeFunctionData(
    functionFragment: "execute",
    values: [ConduitTransferStruct[]]
  ): string;
  encodeFunctionData(
    functionFragment: "executeBatch1155",
    values: [ConduitBatch1155TransferStruct[]]
  ): string;
  encodeFunctionData(
    functionFragment: "executeWithBatch1155",
    values: [ConduitTransferStruct[], ConduitBatch1155TransferStruct[]]
  ): string;
  encodeFunctionData(
    functionFragment: "updateChannel",
    values: [string, boolean]
  ): string;

  decodeFunctionResult(functionFragment: "execute", data: BytesLike): Result;
  decodeFunctionResult(
    functionFragment: "executeBatch1155",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "executeWithBatch1155",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "updateChannel",
    data: BytesLike
  ): Result;

  events: {
    "ChannelUpdated(address,bool)": EventFragment;
  };

  getEvent(nameOrSignatureOrTopic: "ChannelUpdated"): EventFragment;
}

export interface ChannelUpdatedEventObject {
  channel: string;
  open: boolean;
}
export type ChannelUpdatedEvent = TypedEvent<
  [string, boolean],
  ChannelUpdatedEventObject
>;

export type ChannelUpdatedEventFilter = TypedEventFilter<ChannelUpdatedEvent>;

export interface ConduitMock extends BaseContract {
  connect(signerOrProvider: Signer | Provider | string): this;
  attach(addressOrName: string): this;
  deployed(): Promise<this>;

  interface: ConduitMockInterface;

  queryFilter<TEvent extends TypedEvent>(
    event: TypedEventFilter<TEvent>,
    fromBlockOrBlockhash?: string | number | undefined,
    toBlock?: string | number | undefined
  ): Promise<Array<TEvent>>;

  listeners<TEvent extends TypedEvent>(
    eventFilter?: TypedEventFilter<TEvent>
  ): Array<TypedListener<TEvent>>;
  listeners(eventName?: string): Array<Listener>;
  removeAllListeners<TEvent extends TypedEvent>(
    eventFilter: TypedEventFilter<TEvent>
  ): this;
  removeAllListeners(eventName?: string): this;
  off: OnEvent<this>;
  on: OnEvent<this>;
  once: OnEvent<this>;
  removeListener: OnEvent<this>;

  functions: {
    execute(
      arg0: ConduitTransferStruct[],
      overrides?: CallOverrides
    ): Promise<[string]>;

    executeBatch1155(
      arg0: ConduitBatch1155TransferStruct[],
      overrides?: CallOverrides
    ): Promise<[string] & { magicValue: string }>;

    executeWithBatch1155(
      arg0: ConduitTransferStruct[],
      arg1: ConduitBatch1155TransferStruct[],
      overrides?: CallOverrides
    ): Promise<[string] & { magicValue: string }>;

    updateChannel(
      channel: string,
      isOpen: boolean,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;
  };

  execute(
    arg0: ConduitTransferStruct[],
    overrides?: CallOverrides
  ): Promise<string>;

  executeBatch1155(
    arg0: ConduitBatch1155TransferStruct[],
    overrides?: CallOverrides
  ): Promise<string>;

  executeWithBatch1155(
    arg0: ConduitTransferStruct[],
    arg1: ConduitBatch1155TransferStruct[],
    overrides?: CallOverrides
  ): Promise<string>;

  updateChannel(
    channel: string,
    isOpen: boolean,
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  callStatic: {
    execute(
      arg0: ConduitTransferStruct[],
      overrides?: CallOverrides
    ): Promise<string>;

    executeBatch1155(
      arg0: ConduitBatch1155TransferStruct[],
      overrides?: CallOverrides
    ): Promise<string>;

    executeWithBatch1155(
      arg0: ConduitTransferStruct[],
      arg1: ConduitBatch1155TransferStruct[],
      overrides?: CallOverrides
    ): Promise<string>;

    updateChannel(
      channel: string,
      isOpen: boolean,
      overrides?: CallOverrides
    ): Promise<void>;
  };

  filters: {
    "ChannelUpdated(address,bool)"(
      channel?: string | null,
      open?: null
    ): ChannelUpdatedEventFilter;
    ChannelUpdated(
      channel?: string | null,
      open?: null
    ): ChannelUpdatedEventFilter;
  };

  estimateGas: {
    execute(
      arg0: ConduitTransferStruct[],
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    executeBatch1155(
      arg0: ConduitBatch1155TransferStruct[],
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    executeWithBatch1155(
      arg0: ConduitTransferStruct[],
      arg1: ConduitBatch1155TransferStruct[],
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    updateChannel(
      channel: string,
      isOpen: boolean,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;
  };

  populateTransaction: {
    execute(
      arg0: ConduitTransferStruct[],
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    executeBatch1155(
      arg0: ConduitBatch1155TransferStruct[],
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    executeWithBatch1155(
      arg0: ConduitTransferStruct[],
      arg1: ConduitBatch1155TransferStruct[],
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    updateChannel(
      channel: string,
      isOpen: boolean,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;
  };
}
