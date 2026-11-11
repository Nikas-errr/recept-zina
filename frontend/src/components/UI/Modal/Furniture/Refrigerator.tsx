import { cn } from "@/lib/utils"
import Image from "next/image"
import { useState } from "react"

import openRefrigerator from '../../../../../public/openRefrigerator.png'
import { ClipLoaderUI } from "@/components/UI/ClipLoader"
import { Products } from "./Products"
import { useGetIngredient } from "@/hooks/Ingredient"

type Props = {
    error: boolean,
    setError: (value: boolean) => void
}

export function Refrigerator({ error, setError }: Props) {
    const [value, setValue] = useState<string>('')
    const { listIngredient, loading, error: loadError } = useGetIngredient('refrigerator')

    const search = value.trim().toLowerCase()
    const list = (listIngredient ?? []).filter(item =>
        !search ||
        item.name.toLowerCase().includes(search) ||
        item.slug.toLowerCase().includes(search)
    )

    return (
        <div className={cn(
            'transition-[height] duration-300',
            'relative w-[540px] flex flex-col gap-y-[20px]',
            'bg-white p-[20px] rounded-2xl',
            error ? 'h-[750px]' : 'h-[710px]'
        )}>
            <Image src={openRefrigerator} alt='' draggable='false'
                className={cn(
                    'w-[500px] h-[600px] transition-[top] duration-300 ease-out',
                    'z-10 absolute left-[20px]',
                    error ? 'top-[130px]' : 'top-[90px]'
                )} />
            <div className=''>
                <input value={value} onChange={e => setValue(e.target.value)}
                    spellCheck='false'
                    className={cn(
                        'w-full h-[50px] rounded-2xl border border-gray-200 bg-gray-100',
                        'text-[18px] font-light pl-[20px] pr-[50px]',
                        'outline-0',
                    )} placeholder='Название продукта' />
            </div>
            <div className={cn(
                'text-[16px] text-red-400',
                'transition-[opacity,height] duration-300',
                error ? 'opacity-100 h-[20px]' : 'opacity-0 h-0'
            )}>
                Можно выбрать не больше 4 ингредиентов
            </div>
            {loading
                ? <div className='text-gray-400 pl-[50px]'>Загрузка...</div>
                : <>
                    {loadError && (
                        <div className='text-red-500 pl-[50px] text-[14px] break-all'>
                            Ошибка загрузки: {loadError.message}
                        </div>
                    )}
                    {!loadError && list.length === 0 && (
                        <div className='text-gray-400 pl-[50px]'>Продукты не найдены</div>
                    )}
                    <Products setError={setError} height={600} paddingTop={30} paddingBottom={30}
                        paddingX={50} listProducts={list} />
                </>}
        </div>
    )
}
