'use client'

import { useState } from "react"
import { cn } from "@/lib/utils"
import useIngredients from "@/store/Ingredients/useIngredients"
import { axiosInstance } from "@/services/instance"

type Recipe = {
    id: string
    title: string
    imageUrl: string | null
    ingredients: { name: string, amount: string }[]
    steps: string[]
}

export function Btn() {
    const { ingredients } = useIngredients((state) => state)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [message, setMessage] = useState('')
    const [recipes, setRecipes] = useState<Recipe[]>([])

    const findRecipes = async () => {
        if (!ingredients.length || loading) return
        setLoading(true)
        setError('')
        setRecipes([])
        setMessage('')
        try {
            const { data } = await axiosInstance.post('/api/recipes/search', {
                ingredients: ingredients.map(i => i.slug),
                avoid: [],
            })
            setRecipes(data.recipes ?? [])
            if (!data.recipes?.length) setMessage(data.message ?? 'Рецепты не найдены')
        } catch (err: any) {
            setError(err?.response?.data?.message ?? 'Не удалось получить рецепты')
        } finally {
            setLoading(false)
        }
    }

    return (
        <>
            <div className={cn(
                'w-[200px] mx-auto h-[50px] rounded-2xl bg-blue-500 flex items-center justify-center',
                'text-white text-[18px] font-light',
                'hover:translate-y-[-2px] transition-transform duration-300 cursor-pointer'
            )} onClick={findRecipes}>
                {loading ? 'Ищем...' : 'Найти рецепты!'}
            </div>
            {(recipes.length > 0 || message || error) && (
                <div className={cn(
                    'fixed right-[20px] top-[20px] z-50 w-[440px] max-h-[85vh] overflow-auto',
                    'bg-white rounded-2xl p-[20px] shadow-2xl flex flex-col gap-y-[14px]'
                )}>
                    <div className='flex items-center justify-between'>
                        <div className='text-[18px]'>Рецепты ({recipes.length})</div>
                        <div className='text-gray-400 cursor-pointer text-[14px]'
                            onClick={() => { setRecipes([]); setMessage(''); setError('') }}>
                            Закрыть
                        </div>
                    </div>
                    {error && <div className='text-red-500'>{error}</div>}
                    {message && <div className='text-gray-500'>{message}</div>}
                    {recipes.map(r => (
                        <div key={r.id} className='border border-gray-100 rounded-2xl p-[14px] flex gap-x-[12px]'>
                            {r.imageUrl && (
                                <img src={r.imageUrl} alt='' className='w-[90px] h-[90px] rounded-xl object-cover' />
                            )}
                            <div className='flex flex-col gap-y-[6px]'>
                                <div className='font-medium'>{r.title}</div>
                                <div className='text-[13px] text-gray-500'>
                                    Ингредиентов: {r.ingredients.length} | Шагов: {r.steps.length}
                                </div>
                                {r.steps[0] && <div className='text-[12px] text-gray-400'>{r.steps[0]}</div>}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </>
    )
}
