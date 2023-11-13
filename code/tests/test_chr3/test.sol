// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;


//solmate#161
abstract contract ERC721 {
    mapping(uint256 => address) internal ownerOf;

    uint256 ID = 0;
    uint256 ID1 = 1;
    uint256 ID2 = 2;

    event Transfer(address from, address to, uint256 id);

    function _burn0(uint256 id) internal virtual {
        address owner = ownerOf[id];
        require(ownerOf[id] != address(0), "NOT_MINTED");
        delete ownerOf[id];
        emit Transfer(owner, address(0), id);
    }

    function _burn1(uint256 id) internal virtual {
        address owner = ownerOf[id];

        if(id > 100) {
            ownerOf[id] = address(100);
        }

        require(ownerOf[id] != address(0), "NOT_MINTED");
        delete ownerOf[id];

        emit Transfer(owner, address(0), id);
    }


    function _burn2(uint256 id) internal virtual {
        address owner = ownerOf[id];
        id += 1;
        require(ownerOf[id] != address(0), "NOT_MINTED");
        delete ownerOf[id];

        emit Transfer(owner, address(0), id);
    }

    function _burn3(uint256 id) internal virtual {
        address owner = ownerOf[id];
        if(id > 100) {
            id += 1;
        }
        require(ownerOf[id] != address(0), "NOT_MINTED");
        delete ownerOf[id];

        emit Transfer(owner, address(0), id);
    }

    function _burn4(uint256 id) internal virtual {
        address owner = ownerOf[id];
        uint256 i = ID;
        ID += 1;
        if(id > 100) {
            ID = 2;
            ownerOf[id] = address(1);
            owner = ownerOf[ID];
        }
        emit Transfer(owner, address(0), ID);
        require(ownerOf[id] != address(0), "NOT_MINTED");
        delete ownerOf[id];

        emit Transfer(owner, address(0), id);
    }

    function _burn5(uint256 id) internal virtual {
        uint256 i = ID;
        if(id > 100) {
            ID = 2;
            ownerOf[id] = address(1);
            address a = ownerOf[id];
            ID = 10;
        }
        //ID += 1;
        emit Transfer(address(1), address(0), ID);
    }

    function _burn6(uint256 id) internal virtual {
        uint256 i = ID;
        if(id > 100) {
            ID = 2;
        } else {
           ID += 1;
        }
        emit Transfer(address(1), address(0), ID);
    }

    function _burn7(uint256 id) internal virtual {
        uint256 i = ID;
        if(id > 100) {
            ID = 2;
        } else {
           emit Transfer(address(1), address(0), ID);
        }
        emit Transfer(address(1), address(0), ID);
    }

    function _burn8(uint256 id) internal virtual {
        uint256 i = ID1;
        if(id > 100) {
            ID2 = 2;
        } else {
           ID1 += ID1;
        }
        emit Transfer(address(1), address(0), ID);
        emit Transfer(address(1), address(0), ID2);
        emit Transfer(address(1), address(0), ID1);
    }

    function _burn9(uint256 id) internal virtual {
        uint256 i = ID1;
        while(i>0) {
            ID1 += 1;
            emit Transfer(address(1), address(0), ID);
            i --;
        }
        
    }
}