// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

library StringUtil {
    function concat(string memory str1, string memory str2) internal pure returns (string memory) {
        bytes memory bytesStr1 = bytes(str1);
        bytes memory bytesStr2 = bytes(str2);
        bytes memory result = new bytes(bytesStr1.length + bytesStr2.length);

        for (uint256 i = 0; i < bytesStr1.length; i++) {
            result[i] = bytesStr1[i];
        }

        for (uint256 j = 0; j < bytesStr2.length; j++) {
            result[bytesStr1.length + j] = bytesStr2[j];
        }

        return string(result);
    }

    function toStr(uint256 value) internal pure returns (string memory) {
        if (value == 0) {
            return "0";
        }

        uint256 temp = value;
        uint256 digits;

        while (temp != 0) {
            digits++;
            temp /= 10;
        }

        bytes memory buffer = new bytes(digits);

        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }

        return string(buffer);
    }
}