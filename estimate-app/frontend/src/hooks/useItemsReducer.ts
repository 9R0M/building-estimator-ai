// src/hooks/useItemsReducer.ts

import { useReducer } from 'react';

export interface Item {
    description: string;
    quantity: number;
    unitPrice: number;
    error?: string;
}

type State = Item[];
type Action =
    | { type: 'CHANGE'; idx: number; key: keyof Item; value: string | number }
    | { type: 'ADD' }
    | { type: 'REMOVE'; idx: number }
    | { type: 'SUBMIT' };

function validateField(key: keyof Item, value: string | number): string | undefined {
    if (key === 'description') return value ? undefined : '内容を入力してください';
    if (key === 'quantity' || key === 'unitPrice') {
        const num = Number(value);
        return num > 0 && !isNaN(num) ? undefined : '正の数字を入力してください';
    }
}

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case 'CHANGE':
            return state.map((it, i) =>
                i !== action.idx
                    ? it
                    : { ...it, [action.key]: action.value, error: validateField(action.key, action.value) }
            );
        case 'ADD':
            return [...state, { description: '', quantity: 1, unitPrice: 0, error: '内容を入力してください' }];
        case 'REMOVE':
            return state.filter((_, i) => i !== action.idx);
        default:
            return state;
    }
}

export function useItems() {
    const [items, dispatch] = useReducer(reducer, []);

    const change = (idx: number, key: keyof Item, value: string | number) =>
        dispatch({ type: 'CHANGE', idx, key, value });
    const add = () => dispatch({ type: 'ADD' });
    const remove = (idx: number) => dispatch({ type: 'REMOVE', idx });
    const isValid = () => items.length > 0 && items.every(it => !it.error && it.description);

    return { items, change, add, remove, isValid, dispatch };
}