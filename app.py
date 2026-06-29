import streamlit as st
import google.generativeai as genai

# 새로 발급받은 API 키를 여기에 입력하세요
api_key = "AQ.Ab8RN6IaRAAIT7Ej7iuqNxbBkFGTHZSSzPq3VD94c52iR080mw"
genai.configure(api_key=api_key)

st.set_page_config(page_title="Trend-Catcher", page_icon="🚀", layout="centered")
st.title("🚀 Trend-Catcher : 반도체 트렌드 큐레이터")
st.markdown("쏟아지는 반도체/디스플레이 정보 속에서 **핵심 기술 트렌드**만 필터링합니다.")

menu = st.radio(
    "분석 메뉴를 선택하세요:", 
    ["1. 데일리 기술 브리핑 (최근 24H)", "2. 관련 수혜주 및 밸류체인 분석", "3. 주간 핫이슈 (최근 7D)"]
)

if st.button("분석 실행", type="primary"):
    with st.spinner("최적의 AI 모델을 찾아 실시간 분석을 진행 중입니다..."):
        try:
            # 1단계: 프롬프트 세팅
            if "1. 데일리" in menu:
                prompt = """
                최근 24시간 이내의 반도체 공정/장비/기술 관련 최신 뉴스 3개를 요약해 줘.
                
                [출력 형식]
                ### 📰 [기사 제목]
                * **🔗 관련 정보:** [[언론사명 | 발행일자] 정확한 기사 제목]
                * **💡 핵심 요약:** (기술적 맥락과 산업적 영향 중심 3줄 개조식)
                """
            elif "2. 관련 수혜주" in menu:
                prompt = """
                최근 반도체 장비 및 소재 분야의 최신 기술 트렌드를 바탕으로, 실제 수혜가 예상되는 소부장(소재/부품/장비) 상장 기업 1~2곳을 분석해 줘.
                주가 등락보다는 '어떤 공정/기술을 가졌기에 수혜를 받는지' 공학적 관점에서 설명해.
                
                [출력 형식]
                ### 🎯 추천 밸류체인: [기업명]
                * **💡 기술적 분석 이유:** (공학적 관점과 주력 사업 연결)
                * **🔗 관련 정보:** [[언론사명 | 발행일자] 해당 기업 관련 기사 제목]
                """
            else:
                prompt = """
                최근 1주일 동안 파급력이 컸던 반도체/디스플레이 기계/장비 설계 핵심 이슈 3개를 찾아 요약해 줘.
                
                [출력 형식]
                ### 📰 [기사 제목]
                * **🔗 관련 정보:** [[언론사명 | 발행일자] 정확한 기사 제목]
                * **💡 핵심 요약:** (기술적 맥락 중심 3줄 개조식)
                """
            
            # 2단계: API 키가 진짜로 쓸 수 있는 모델 목록만 서버에서 직접 가져오기 (404 원천 차단)
            available_models = []
            try:
                for m in genai.list_models():
                    # gemini가 포함된 텍스트/대화형 모델만 수집
                    if 'gemini' in m.name and 'vision' not in m.name:
                        available_models.append(m.name.replace('models/', ''))
            except Exception:
                # 목록 조회 실패 시 최후의 비상용 리스트
                available_models = ['gemini-1.5-flash-8b', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro']
            
            # 처리 속도가 빠른 flash 모델부터 시도하도록 정렬
            available_models = sorted(available_models, key=lambda x: ('flash' not in x, x))

            response_text = None
            used_model_info = None
            last_error = ""
            
            # 3단계: 허락된 모델을 순차적으로 시도하는 불패의 루프
            for model_name in available_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    
                    # 1차 시도: 구글 검색 도구 켜고 실행
                    try:
                        response = model.generate_content(prompt, tools='google_search_retrieval')
                        response_text = response.text
                        used_model_info = f"{model_name} (실시간 검색 작동)"
                        break # 성공 시 즉시 루프 탈출
                    
                    except Exception:
                        # 2차 시도: 검색 도구가 막혀있다면, 일반 모델로 즉시 우회 생성
                        response = model.generate_content(prompt)
                        response_text = response.text
                        used_model_info = f"{model_name} (AI 기본 지식 작동)"
                        break # 성공 시 즉시 루프 탈출
                        
                except Exception as e:
                    # 해당 모델이 완전히 막혀있으면 다음 모델로 부드럽게 넘어감
                    last_error = str(e)
                    continue 
                    
            # 4단계: 결과 출력
            if response_text:
                st.markdown(response_text)
                # 성공적으로 작동한 모델의 이름을 하단에 슬쩍 보여줍니다. (심사위원 어필용)
                st.caption(f"✓ 구동 정보: {used_model_info}로 정상 분석되었습니다.")
            else:
                raise Exception(f"허용된 모든 모델이 응답하지 않습니다. (마지막 에러: {last_error})")
            
        except Exception as e:
            # 모든 시도가 실패했을 때만 최후의 에러 띄움
            st.error(f"🚨 시스템 오류: {e}")
            st.info("💡 모든 구동 시도가 실패했습니다. API 키의 서비스 접근 권한이 완전히 막혀있는지 확인이 필요합니다.")