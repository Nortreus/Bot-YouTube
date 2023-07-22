#Importação de bibliotecas
#Utilizada pra acessa a API
from googleapiclient.discovery import build
#Utilizada para tratamento de erros
from googleapiclient.errors import HttpError
#Utilizada para manipulação de estruturas de dados
import pandas as pd
#Utilizada para a criação de uma tabela visual no prompt
from tabulate import tabulate
#Utilizada para conversão dos valores iso retornados
from isodate import parse_duration

#Sua chave API encontrada na pagina do seu projeto no Google Cloud
API_KEY = ''

#Função para fazer uma requisição e retornar os valores de duração de videos utilizados nos parametros de pesquisa
def get_video_duration(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    video_response = youtube.videos().list(
        part='contentDetails',
        id=video_id
    ).execute()

    duration_iso = video_response['items'][0]['contentDetails']['duration']
    duration = str(parse_duration(duration_iso))
    return duration

#Função para fazer a busca de videos pelos parametros estabelecidos
def search_videos_by_topic(topic, duration, min_views, min_subs, region_code, relevance_language):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    try:
        #Realiza a pesquisa no YouTube com os parâmetros de língua e localidade
        search_response = youtube.search().list(
            q=topic,
            part='snippet',
            type='video',
            videoDuration=duration,
            maxResults=100,
            regionCode=region_code,
            relevanceLanguage=relevance_language,
            order='relevance'          
        ).execute()

        #Cria uma lista para armazenar os dados dos vídeos
        videos_data = []
        
        # Obtém informações sobre os vídeos encontrados
        for item in search_response['items']:
            video_id = item['id']['videoId']
            video_response = youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()

            video_info = video_response['items'][0]
            views = int(video_info['statistics']['viewCount'])
            title = video_info['snippet']['title']
            published_at = video_info['snippet']['publishedAt']
            channel_id = video_info['snippet']['channelId']
            duration = get_video_duration(video_id)
            
            # Obtém informações do canal
            channel_response = youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()

            channel_info = channel_response['items'][0]
            channel_title = channel_info['snippet']['title']
            subs = int(channel_info['statistics']['subscriberCount'])

            if views >= min_views and subs >= min_subs:
                videos_data.append([title, views, duration, published_at, channel_title, subs])
                
        #Cria um DataFrame pandas com os dados dos vídeos
        df = pd.DataFrame(videos_data, columns=['Título', 'Visualizações','Duração', 'Publicado em', 'Canal', 'Inscritos'])

        #Exibe a tabela formatada
        print(tabulate(df, headers='keys', tablefmt='grid'))    
        
    except HttpError as e:
        print(f"Erro ao pesquisar e obter informações sobre os vídeos: {e}")

#Onde seração colocados os parametros de busca
if __name__ == '__main__':
    search_videos_by_topic('Topico','any', 100000, 100000, 'br', 'pt')
