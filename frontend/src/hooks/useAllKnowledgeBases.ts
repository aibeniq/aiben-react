import { useQuery } from "@tanstack/react-query"
import { KnowledgeBasesService } from "../client"

interface UseAllKnowledgeBasesReturn {
    knowledgeBases: any[]
    isLoading: boolean
}

export const useAllKnowledgeBases = (): UseAllKnowledgeBasesReturn => {
    // Knowledge bases query - always fetches ALL users' knowledge bases
    const knowledgeBasesQuery = useQuery({
        queryKey: ["all-knowledge-bases"],
        queryFn: async () => {
            console.log(
                "🔄 ALL-KNOWLEDGE-BASES: Starting to fetch all knowledge bases",
            )
            const response = await KnowledgeBasesService.readKnowledgeBases({
                limit: 1000, // Fetch more records
                show_all: true, // Always show all users' knowledge bases
            })
            console.log(
                "✅ ALL-KNOWLEDGE-BASES: Fetch completed, response:",
                response,
            )
            console.log(
                "📊 ALL-KNOWLEDGE-BASES: Number of knowledge bases returned:",
                response?.data?.length || 0,
            )
            return response?.data || []
        },
        enabled: true,
    })

    return {
        knowledgeBases: knowledgeBasesQuery.data || [],
        isLoading: knowledgeBasesQuery.isLoading,
    }
}
