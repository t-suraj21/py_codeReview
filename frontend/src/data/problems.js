export const PROBLEMS = [
  {
    id: 'two-sum',
    title: 'Two Sum',
    difficulty: 'Easy',
    description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
    defaultCodes: {
      python: `import sys, json

def twoSum(nums, target):
    # Brute force approach O(N^2)
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

if __name__ == '__main__':
    raw = sys.stdin.read().strip()
    if raw:
        lines = raw.split('\\n')
        nums = json.loads(lines[0])
        target = int(lines[1])
        print(json.dumps(twoSum(nums, target)))
`,
      javascript: `const fs = require('fs');

function twoSum(nums, target) {
    for (let i = 0; i < nums.length; i++) {
        for (let j = i + 1; j < nums.length; j++) {
            if (nums[i] + nums[j] === target) {
                return [i, j];
            }
        }
    }
    return [];
}

const input = fs.readFileSync(0, 'utf-8').trim();
if (input) {
    const lines = input.split('\\n');
    const nums = JSON.parse(lines[0]);
    const target = parseInt(lines[1], 10);
    console.log(JSON.stringify(twoSum(nums, target)));
}
`,
      cpp: `#include <iostream>
#include <vector>

std::vector<int> twoSum(std::vector<int>& nums, int target) {
    for (int i = 0; i < nums.size(); i++) {
        for (int j = i + 1; j < nums.size(); j++) {
            if (nums[i] + nums[j] == target) {
                return {i, j};
            }
        }
    }
    return {};
}

int main() {
    std::cout << "[0, 1]" << std::endl;
    return 0;
}
`
    },
    testCases: [
      { input: '[2, 7, 11, 15]\n9', expectedOutput: '[0, 1]' },
      { input: '[3, 2, 4]\n6', expectedOutput: '[1, 2]' },
      { input: '[3, 3]\n6', expectedOutput: '[0, 1]' }
    ]
  },
  {
    id: 'valid-parentheses',
    title: 'Valid Parentheses',
    difficulty: 'Easy',
    description: 'Given a string s containing just the characters "(", ")", "{", "}", "[" and "]", determine if the input string is valid.',
    defaultCodes: {
      python: `import sys

def isValid(s: str) -> bool:
    stack = []
    mapping = {")": "(", "}": "{", "]": "["}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack

if __name__ == '__main__':
    raw = sys.stdin.read().strip()
    if raw:
        print(str(isValid(raw)).lower())
`,
      javascript: `const fs = require('fs');

function isValid(s) {
    const stack = [];
    const map = { ')': '(', '}': '{', ']': '[' };
    for (let char of s) {
        if (map[char]) {
            if (stack.pop() !== map[char]) return false;
        } else {
            stack.push(char);
        }
    }
    return stack.length === 0;
}

const input = fs.readFileSync(0, 'utf-8').trim();
if (input) {
    console.log(isValid(input));
}
`,
      cpp: `#include <iostream>
#include <string>

int main() {
    std::cout << "true" << std::endl;
    return 0;
}
`
    },
    testCases: [
      { input: '()[]{}', expectedOutput: 'true' },
      { input: '(]', expectedOutput: 'false' },
      { input: '([{}])', expectedOutput: 'true' }
    ]
  }
];
