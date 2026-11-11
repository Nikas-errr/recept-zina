'use client'

import { useState } from "react"
import { cn } from "@/lib/utils"
import { signIn } from "next-auth/react"

export function SignIn() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')

    const loginByEmail = async () => {
        setError('')
        const res = await signIn('credentials', { email, password, redirect: false })
        if (res?.error) {
            setError('Неверный email или пароль')
        } else {
            window.location.href = '/'
        }
    }

    return (
        <div className='flex flex-col gap-y-[10px] w-full'>
            <input className={cn(
                'h-[46px] rounded-2xl border border-gray-200 bg-gray-100 px-[16px] outline-0'
            )} placeholder='Email' value={email} onChange={e => setEmail(e.target.value)} />
            <input className={cn(
                'h-[46px] rounded-2xl border border-gray-200 bg-gray-100 px-[16px] outline-0'
            )} placeholder='Пароль (от 8 символов)' type='password'
                value={password} onChange={e => setPassword(e.target.value)} />
            {error && <div className='text-red-500 text-[14px]'>{error}</div>}
            <div className={cn(
                'bg-blue-500 text-white text-center py-[12px] rounded-2xl cursor-pointer',
                'hover:translate-y-[-2px] transition-transform'
            )} onClick={loginByEmail}>
                Войти
            </div>
            <div className='text-[13px] text-gray-400 text-center'>
                Нет аккаунта? <a className='underline' href='/signUp'>Зарегистрируйся</a>
            </div>
            <div className={cn(
                'relative flex items-center gap-x-[20px] bg-white py-[10px] px-[20px] rounded-2xl',
                'hover:translate-y-[2px] transition-transform duration-300 cursor-pointer'
            )} onClick={() => signIn('google', { callbackUrl: '' })}>
                <div className='w-full text-center'>Google</div>
            </div>
            <div className={cn(
                'relative flex items-center gap-x-[20px] bg-[#F6F8FA] py-[10px] px-[20px] rounded-2xl',
                'hover:translate-y-[2px] transition-transform duration-300 cursor-pointer'
            )} onClick={() => signIn('github', { callbackUrl: '' })}>
                <div className='text-[#24292F] w-full text-center'>GitHub</div>
            </div>
        </div>
    )
}
