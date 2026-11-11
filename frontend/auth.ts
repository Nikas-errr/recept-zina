import GitHub from "next-auth/providers/github"
import Google from "next-auth/providers/google"
import Credentials from "next-auth/providers/credentials"

import NextAuth from "next-auth"
import { api } from "@/app/api/client"

type LoginResponse = {
    access_token: string
    token_type: string
    user: {
        id: string
        email: string
    }
}

export const { handlers, auth, signIn, signOut } = NextAuth({
    providers: [
        Google, GitHub,
        Credentials({
            credentials: {
                email: { label: 'Email', type: 'email' },
                password: { label: 'Password', type: 'password' }
            },

            async authorize(credentials) {
                if (!credentials.email || !credentials.password) {
                    return null
                }

                try {
                    const { data } = await api.post<LoginResponse>('/auth/login', {
                        email: credentials.email,
                        password: credentials.password
                    })

                    if (!data?.user) return null

                    return {
                        id: String(data.user.id),
                        email: data.user.email,
                        accessToken: data.access_token
                    }

                } catch (error) {
                    console.error('Ошибка входа:', error)
                    return null
                }
            },
        })
    ],
    session: { strategy: 'jwt' },
    trustHost: true,
    callbacks: {
        async jwt({ token, user }) {
            if (user) {
                token.id = user.id
                token.accessToken = user.accessToken
            }
            return token
        },
        async session({ session, token }) {
            if (session.user) {
                session.user.id = token.id as string
                session.user.accessToken = token.accessToken as string | undefined
            }
            return session
        },
    },
})
