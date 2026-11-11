'use client'

import { useState } from 'react'
import { axiosInstance } from '@/services/instance'

export default function page() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [done, setDone] = useState(false)

    const register = async () => {
        setError('')
        try {
            await axiosInstance.post('/api/auth/register', { email, password })
            setDone(true)
        } catch (err: any) {
            setError(err?.response?.data?.message ?? 'Ошибка регистрации')
        }
    }

    return (
        <div className='max-w-[420px] mx-auto mt-[100px] bg-white rounded-2xl p-[24px] flex flex-col gap-y-[12px]'>
            <div className='text-[22px] font-medium'>Регистрация</div>
            <input className='h-[46px] rounded-xl border border-gray-200 bg-gray-100 px-[14px] outline-0'
                placeholder='Email' value={email} onChange={e => setEmail(e.target.value)} />
            <input className='h-[46px] rounded-xl border border-gray-200 bg-gray-100 px-[14px] outline-0'
                placeholder='Пароль (от 8 символов)' type='password'
                value={password} onChange={e => setPassword(e.target.value)} />
            <button className='h-[46px] rounded-xl bg-blue-500 text-white cursor-pointer'
                onClick={register}>
                Зарегистрироваться
            </button>
            {done && <div className='text-green-600'>Готово! Теперь войди на странице /signIn</div>}
            {error && <div className='text-red-500'>{error}</div>}
            <div className='text-[13px] text-gray-400'>Уже есть аккаунт? <a className='underline' href='/signIn'>Войти</a></div>
        </div>
    )
}
