from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from duckduckgo_search import DDGS, AsyncDDGS
from searchendgine.models import APIKeyHandel
import asyncio

class DuckDuckAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        search_type = request.query_params.get('type', 'text')
        region = request.query_params.get('region', 'wt-wt')
        safesearch = request.query_params.get('safesearch', 'off')
        timelimit = request.query_params.get('timelimit', 'y')
        max_results = int(request.query_params.get('max_results', 10))

        size = request.query_params.get('size')
        color = request.query_params.get('color')
        type_image = request.query_params.get('type_image')
        layout = request.query_params.get('layout')
        license_image = request.query_params.get('license_image')

        if not query:
            return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        

        if search_type not in ['text', 'pdf', 'video', 'image']:
            return Response({"error": "Invalid search type"}, status=status.HTTP_400_BAD_REQUEST)
        if APIKeyHandel.objects.filter(is_live=True):
                
            try:
                if search_type == 'text':
                    results = DDGS().text(query, region=region, safesearch=safesearch, timelimit=timelimit, max_results=max_results)
                    return Response(list(results), status=status.HTTP_200_OK)
                elif search_type == 'pdf':
                    results = DDGS().text(f"{query} filetype:pdf", region=region, safesearch=safesearch, timelimit=timelimit, max_results=max_results)
                    return Response(list(results), status=status.HTTP_200_OK)
                elif search_type == 'video':
                    async def fetch_videos():
                        return await AsyncDDGS().avideos(query, region=region, safesearch=safesearch, timelimit=timelimit, max_results=max_results)
                    results = asyncio.run(fetch_videos())
                    
                    processed_results = []
                    for result in results:
                        processed_result = result.copy()
                        if 'images' in processed_result:
                            processed_result['image_urls'] = processed_result['images']
                            del processed_result['images']
                        processed_results.append(processed_result)
                    
                    return Response(processed_results, status=status.HTTP_200_OK)
                elif search_type == 'image':
                    async def fetch_images():
                        return await AsyncDDGS().aimages(
                            keywords=query,
                            region=region,
                            safesearch=safesearch,
                            size=size,
                            color=color,
                            type_image=type_image,
                            layout=layout,
                            license_image=license_image,
                            max_results=max_results
                        )
                    results = asyncio.run(fetch_images())
                    return Response(list(results), status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            return Response({'message':'API key expired'}, 400)