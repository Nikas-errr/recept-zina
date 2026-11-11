import { cn } from "@/lib/utils"
import { useRef, useState } from "react"
import { Wardrobe } from "./Furniture/Wardrobe"
import { Refrigerator } from "./Furniture/Refrigerator"
import { useClickAway } from "react-use"
import { useEscape } from "@/hooks/useEscape"

type Props = {
    showModal: boolean,
    setShowModal: (value: boolean) => void
}

export function Modal({ showModal, setShowModal }: Props) {
    const [error, setError] = useState<boolean>(false)

    const ref = useRef<HTMLDivElement>(null)

    useClickAway(ref, () => setShowModal(false))
    useEscape(() => setShowModal(false))

    return (
        <div className={cn(
            showModal
                ? [
                    'z-10 fixed top-0 left-0 w-full h-screen bg-black/50',
                    'flex items-center justify-center'
                ]
                : 'hidden'
        )}>
            {/* Мебель создаётся при каждом открытии: каждый раз свежий запрос в API */}
            {showModal && (
                <div ref={ref} className='w-fit h-fit flex items-center justify-center gap-x-[50px]'>
                    <Wardrobe error={error} setError={setError} />
                    <Refrigerator error={error} setError={setError} />
                </div>
            )}
        </div>
    )
}