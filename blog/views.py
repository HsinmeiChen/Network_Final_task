
import configparser
from django.shortcuts import render, redirect
from blog import urlProcessor, utility
from blog.models import TeachingSession
from myproject.schema.responseValidation import ValidateResponseRequest,ValidateResponseResponse
from myproject.entity.db.models.conversation import Conversation
from myproject.entity.db.models.users import User
from myproject.utils import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .decorators import custom_login_required   


config = configparser.ConfigParser()
config.read('config.ini')

# 載入教案初始化佇列
teaching_plan_path = config['Docx']['doc']
teaching_plan = load_teaching_plan(teaching_plan_path)
step_queue = initialize_teaching_plan_queue(teaching_plan)
reference_content = read_docx_content('reference.docx');
max_fail_count = 2
force_to_end_count = 10
# 定義需要處理的 type 列表
valid_response_types = [
    "Relevant Greeting", "Constructive Criticism Response", "Appreciative Response",
    "Positive Response", "Neutral Response"
]

def logout_view(request):
    remove_teaching_session(request)
    return redirect('login')  # 導向需要登入後才能瀏覽的頁面

def login_view(request):
    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        username = userid
        is_valid=True
        # 呼叫自訂驗證函式
        #is_valid, username = User.verify_login(userid, password)
        if is_valid:
            # 驗證成功：可將使用者ID存入 session，或結合 Django auth 系統
            request.session.flush()  # 清除對話數據

            init_teaching_session(request)            
            situation = ask_chatgpt(
                "OpenAI_Completion",
                "以繁體中文生成一個單人被追逐的情境,明確背景設定、角色描述、感官細節、氛圍與情緒、敘事節奏,生成的繁體中文敘述100字以內",
                '繁體中文情境生成,50字以內',
                "以繁體中文生成一個情境",
                model="gpt-4o-mini"
            )
            session = TeachingSession.objects.get(user_id=request.session.session_key)
            session.origin_user_situation = situation
            session.last_user_situation = situation
            session.user_account_name = username
            session.user_account_id=userid
            session.save()
            return redirect('edu_step_view')  # 導向需要登入後才能瀏覽的頁面

    return render(request, 'blog/login.html')

@csrf_exempt  # 禁用 CSRF 驗證，允許 Beacon 請求
def remove_teaching_session(request):
    if request.method == "POST":
        try:
            # 獲取用戶 ID
            data = json.loads(request.body)
            user_id = request.session.session_key
            if not user_id:
                return JsonResponse({"status": "error", "message": "User ID not provided"}, status=400)

            # 刪除 TeachingSession 記錄
            deleted_count, _ = TeachingSession.objects.filter(user_id=user_id).delete()
            
            if deleted_count > 0:
                return JsonResponse({"status": "success", "message": f"Deleted {deleted_count} records"}, status=200)
            else:
                return JsonResponse({"status": "error", "message": "No records found to delete"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


# 檢查否定回應或簡單應答
def contains_negation_or_simple_acknowledgment(user_message):
    negations = ["看完了","不知道", "我不懂", "我不清楚", "no", "No", "沒有","我不知道", "我不會", "不清楚", "不了解", "不明白", "不確定", "沒聽過"]
    acknowledgments = ["好", "ok", "OK", "好的", "嗯", "沒問題", "沒事", "可以", "了解", "瞭解", "看完了"]

    for negation in negations:
        if negation in user_message:
            return True
   
    for acknowledgment in acknowledgments:
        if acknowledgment in user_message:
            return True

    return False

# 修正：從步驟中移除答案的部分
def extract_answer_from_step(step_content):
    # 提取教案 step 中的正確答案，並將其從 step_content 中移除
    if "「" in step_content:
        start = step_content.index("「")
        end = step_content.index("」", start) + 1  # 包含結束括號
        answer = step_content[start + len("「"):end - 1].strip()
        # 移除答案部分，確保括號和答案都被移除
        step_content = step_content[:start].strip() + step_content[end:].strip()
        return answer, step_content  # 返回答案和移除答案後的 step_content
    return None, step_content


# def test_gpt(request):
#     content =  ask_chatgpt(
#     "OpenAI_Completion",
#     inputMsg="test",
#     _assistantName=  'test',
#     assistantInstruction="test",
#     model="gpt-4o-mini"
#     )

#     html_content = f"""
#         <html lang="zh-TW">
#         <head>
#             <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             <title>簡易網頁</title>
#         </head>
#         <body>
#             <h1>{ content }</h1>
#         </body>
#         </html>
#     """    
#     return HttpResponse(html_content)

def generate_TalkToTeacher_Situation():
    return ask_chatgpt(
        "OpenAI_Completion",
        f"學生答題失敗,請學生從頭來過或協尋老師的協助,以浮誇的方式告知,生成的敘述50字以內",
        '繁體中文情境生成',
        "以繁體中文生成一個情境",
        model="gpt-4o-mini"
    )

def generate_Compliment_Situation():
    return ask_chatgpt(
        "OpenAI_Completion",
        f"使用者答題正確,請以浮誇的方式誇獎他,以繁體中文回覆生成的敘述50字以內",
        '繁體中文情境生成',
        "以繁體中文生成一個情境",
        model="gpt-4o-mini"
    )
def generate_Fail_Situation(originSituation,lastSituation):
    return ask_chatgpt(
        "OpenAI_Completion",
        f"初始情境為:'{originSituation}',上一個情境為:'{lastSituation}',生成一個'對逃離不利的因素'並以引號標記,根據上述內容生成一段敘述,生成的敘述50字以內",
        '繁體中文情境生成',
        "以繁體中文生成一個情境",
        model="gpt-4o-mini"
    )

def generate_Correct_Situation(originSituation,lastSituation):
    return ask_chatgpt(
        "OpenAI_Completion",
        f"初始情境為:'{originSituation}',上一個情境為:'{lastSituation}',生成一個'解決不利因素'或'增進逃離的因素'並以引號標記,根據上述內容生成一段敘述,生成的敘述50字以內",
        '繁體中文情境生成',
        "以繁體中文生成一個情境",
        model="gpt-4o-mini"
    )

def generate_Bad_End(originSituation,lastSituation):
    return ask_chatgpt(
        "OpenAI_Completion",
        f"初始情境為:'{originSituation}',上一個情境為:'{lastSituation}',請給一個被捉到的結局,根據上述內容生成一段浮誇的敘述,生成的敘述100字以內",
        '繁體中文情境生成',
        "以繁體中文生成一個情境",
        model="gpt-4o-mini"
    )

def generate_Good_End(originSituation,lastSituation):
    return ask_chatgpt(
        "OpenAI_Completion",
        f"初始情境為:'{originSituation}',上一個情境為:'{lastSituation}',脫離了險況,根據上述內容生成一段結局的敘述,生成的敘述100字以內",
        '繁體中文情境生成',
        "以繁體中文生成一個情境",
        model="gpt-4o-mini"
    )


#@login_required
# Chat 主要功能
@custom_login_required
def chat_view(request):
    if request.method == 'POST':
        conversation = request.session.get('conversation', [])
        user_message = request.POST.get('message', '').strip()
        if user_message:
            conversation.append({"sender": "user", "message": user_message})
            session = TeachingSession.objects.get(user_id=request.session.session_key)

        try:
            if session.current_state == "Guide":
                # 構建 API 請求的輸入
                step_data = step_queue[session.current_step]
                content = step_data.get("content", {})
                question = content.get("Question", {})
                question_description = question.get("Description", "") +"\n" + question.get("Hint", "")
                guidance_directions =  content.get("Guides", {})
                
                if ( len(guidance_directions[session.guide_key]["Answers"])==0 ):   # 不存在Answer時,跳往下一步
                    session.guide_key = get_next_guide_number( session.guide_key, guidance_directions, True)
                    if ( session.guide_key == "-1"):
                        if session.all_fail_count >=10:
                            guide_response = generate_Bad_End(session.origin_user_situation,session.last_user_situation)
                            comfort_response = generate_TalkToTeacher_Situation()                   
                        else:
                            guide_response = generate_Good_End(session.origin_user_situation,session.last_user_situation)
                            comfort_response = generate_Compliment_Situation()
                        session.last_user_situation = guide_response
                        Conversation.async_insert_conversation(
                            session.current_step+1,
                            session.guide_key,
                            session.user_account_id,
                            user_message,
                            gpt_answer_validator_reply=True,
                            fail_count=session.all_fail_count,
                            gpt_answer_feedback="",
                            gpt_feedback=guide_response
                        ) 
                        conversation.append({"sender": "chatgpt", "message": guide_response, "source": "chatgpt"})
                        conversation.append({"sender": "chatgpt", "message": comfort_response, "source": "chatgpt"})                        
                        session.current_step+=1
                        session.guide_key="Guide1"
                        session.current_state="Idle"
                        session.question_displayed=False
                    request.session['conversation'] = conversation
                    session.save()
                    edu_step_view(request)
                    session = TeachingSession.objects.get(user_id=request.session.session_key)
                else:
                    # 呼叫 API
                    api_response = ask_chatgptAPI(
                        "OpenAI_Completion",
                        ValidateResponseRequest(
                            question=guidance_directions[session.guide_key]["Description"],
                            correctAnswer=guidance_directions[session.guide_key]["Answers"],
                            userResponse=user_message,
                            requireAllCorrect=True                        
                        ).model_dump_json(),
                        'ResponseValidation',
                        model="gpt-4o"
                        )
                    validate_response = ValidateResponseResponse(**api_response)
                    # 檢查是否所有 guidanceStatus 的 isFulfilled 為 True
                    if all(answer.isCorrect for answer in validate_response.answers):
                        feedback_response = generate_Correct_Situation(session.origin_user_situation,session.last_user_situation)
                        session.last_user_situation = feedback_response 
                        Conversation.async_insert_conversation( 
                            session.current_step+1,
                            session.guide_key,
                            session.user_account_id,
                            user_message,
                            gpt_answer_validator_reply=True,
                            fail_count=session.all_fail_count,
                            gpt_answer_feedback="\n".join([f"{feedback.feedback}"for feedback in validate_response.answers]),
                            gpt_feedback=feedback_response
                        )
                        conversation.append({"sender": "chatgpt", "message": feedback_response+f"<br><b>[恭喜您答對囉!!, 剩餘生命值為:{(10-session.all_fail_count)*10}]</b>", "source": "chatgpt"})
                        # 更新 session.guide_index 並保存
                        # // ex: Guide1+1 => Guide2
                        session.guide_key = get_next_guide_number( session.guide_key, guidance_directions, True)
                        if ( session.guide_key == "-1"):
                            guide_response = generate_Good_End(session.origin_user_situation,session.last_user_situation)
                            comfort_response = generate_Compliment_Situation()
                            session.last_user_situation = guide_response;
                            Conversation.async_insert_conversation(
                                session.current_step+1,
                                session.guide_key,
                                session.user_account_id,
                                user_message,
                                gpt_answer_validator_reply=True,
                                fail_count=session.all_fail_count,
                                gpt_answer_feedback="",
                                gpt_feedback=guide_response
                            )

                            conversation.append({"sender": "chatgpt", "message": guide_response, "source": "chatgpt"})                            
                            conversation.append({"sender": "chatgpt", "message": comfort_response, "source": "chatgpt"})
                            session.current_step+=1
                            session.current_state="Idle"
                            session.guide_key="Guide1"
                            session.question_displayed=False                                               
                        request.session['conversation'] = conversation
                        session.save()
                        edu_step_view(request)
                        session = TeachingSession.objects.get(user_id=request.session.session_key)
                    else:
                        feedback_response = generate_Fail_Situation(session.origin_user_situation,session.last_user_situation)
                        session.last_user_situation = feedback_response
                        Conversation.async_insert_conversation( 
                            session.current_step+1,
                            session.guide_key,
                            session.user_account_id,
                            user_message,
                            gpt_answer_validator_reply=False,
                            fail_count=session.all_fail_count+1,
                            gpt_answer_feedback="\n".join([f"{feedback.feedback}"for feedback in validate_response.answers]),
                            gpt_feedback=feedback_response
                        )
                        session.all_fail_count +=1
                        conversation.append({"sender": "chatgpt", "message": feedback_response+f"<br><b>[很可惜您答錯了!!, 剩餘生命值為:{(10-session.all_fail_count)*10}]</b>", "source": "chatgpt"})                   
                        if ( session.all_fail_count < 10):
                            if ( session.topic_fail_count < max_fail_count ):                       
                                session.topic_fail_count += 1
                                session.save()
                            else:
                                session.topic_fail_count = 0
                                session.save()
                                if ( session.guide_key+".1" in guidance_directions ):
                                    session.guide_key = session.guide_key+".1"
                                else:
                                    session.guide_key =get_next_guide_number(session.guide_key, guidance_directions, False)
                                    if ( session.guide_key == "-1"):
                                        guide_response = generate_Bad_End(session.origin_user_situation,session.last_user_situation)
                                        comfort_response = generate_TalkToTeacher_Situation()                        
                                        Conversation.async_insert_conversation(
                                            session.current_step+1,
                                            session.guide_key,
                                            session.user_account_id,
                                            user_message,
                                            gpt_answer_validator_reply=False,
                                            fail_count=session.all_fail_count,
                                            gpt_answer_feedback="",
                                            gpt_feedback=guide_response
                                        ) 
                                        conversation.append({"sender": "chatgpt", "message": guide_response, "source": "chatgpt"})
                                        conversation.append({"sender": "chatgpt", "message": comfort_response, "source": "chatgpt"})
                                        session.current_step+=1
                        else:
                            guide_response = generate_Bad_End(session.origin_user_situation,session.last_user_situation)
                            comfort_response = generate_TalkToTeacher_Situation()            
                            Conversation.async_insert_conversation(
                                session.current_step+1,
                                session.guide_key,
                                session.user_account_id,
                                user_message,
                                gpt_answer_validator_reply=False,
                                fail_count=session.all_fail_count,
                                gpt_answer_feedback="",
                                gpt_feedback=guide_response
                            ) 
                            conversation.append({"sender": "chatgpt", "message": guide_response, "source": "chatgpt"})
                            session.current_step+=1                                           
                        request.session['conversation'] = conversation
                        session.save()
                        edu_step_view(request)
                        session = TeachingSession.objects.get(user_id=request.session.session_key)
                        # 計算答對的項目數
                        # correct_count = sum(answer.isCorrect for answer in validate_response.answers)
                        # total_count = len(validate_response.answers)                    
                        # feedback_message = f"您答對了 {correct_count} 個答案，總共需答對 {total_count} 個答案。"
                        # conversation.append({"sender": "chatgpt", "message": feedback_message, "source": "chatgpt"})
            elif session.current_state == "Question":
                # 構建 API 請求的輸入
                step_data = step_queue[session.current_step]
                content = step_data.get("content", {})
                question = content.get("Question", {})
                question_description = question.get("Description", "") +"\n" + question.get("Hint", "")
                api_response = ask_chatgptAPI(
                    "OpenAI_Completion", 
                    ValidateResponseRequest(
                        question=question_description,
                        correctAnswer=[question["Answer"]],
                        userResponse=user_message,
                        requireAllCorrect=True
                    ).model_dump_json(),
                    'ResponseValidation',
                     model="gpt-4o"
                    )
                valid_response = ValidateResponseResponse(**api_response)                       
                if all(answer.isCorrect for answer in valid_response.answers):
                    feedback_response = generate_Correct_Situation(session.origin_user_situation,session.last_user_situation)
                    session.last_user_situation = feedback_response 
                    Conversation.async_insert_conversation( 
                        session.current_step+1,
                        "Guide0",
                        session.user_account_id,
                        user_message,
                        gpt_answer_validator_reply=True,
                        fail_count=session.all_fail_count,
                        gpt_answer_feedback="\n".join([f"{feedback.feedback}"for feedback in valid_response.answers]),
                        gpt_feedback=feedback_response
                    )
                    guide_response = generate_Good_End(session.origin_user_situation,session.last_user_situation)
                    comfort_response = generate_Compliment_Situation()      
                    session.last_user_situation = guide_response;
                    conversation.append({"sender": "chatgpt", "message":feedback_response+f"<br><b>[恭喜您答對囉!!, 剩餘生命值為:{(10-session.all_fail_count)*10}]</b>", "source": "chatgpt"})
                    conversation.append({"sender": "chatgpt", "message":guide_response, "source": "chatgpt"})
                    session.current_step+=1
                    request.session['conversation'] = conversation
                    session.save()
                else :
                    feedback_response = generate_Fail_Situation(session.origin_user_situation,session.last_user_situation)
                    session.last_user_situation = feedback_response 
                    Conversation.async_insert_conversation( 
                        session.current_step+1,
                        "Guide0",
                        session.user_account_id,
                        user_message,
                        gpt_answer_validator_reply=False,
                        fail_count=session.all_fail_count,
                        gpt_answer_feedback="\n".join([f"{feedback.feedback}"for feedback in valid_response.answers]),
                        gpt_feedback=feedback_response
                    )                      

                    session.topic_fail_count = 0
                    session.save()                    
                  
                    conversation.append({"sender": "chatgpt", "message": feedback_response+f"<br><b>[很可惜您答錯了!!, 剩餘生命值為:{(10-session.all_fail_count)*10}]</b>", "source": "chatgpt"})
                edu_step_view(request)

                session = TeachingSession.objects.get(user_id=request.session.session_key)
            else:
                # 如果不是 Guide 狀態，執行通用的對話邏輯
                # chatgpt_response = ask_chatgptAPI(
                #     "OpenAI_Completion",
                #     ClassifyResponseInputNarrative(
                #         narrative=[reference_content],
                #         userResponse=user_message
                #     ).model_dump_json(),
                #     'userResponseClassificationNarrative',
                #     model="gpt-4o-mini"
                # )
                # 檢查並處理回應
                # for response in chatgpt_response.get("responseTypes", []):
                #     #if response.get("type") in valid_response_types:
                #         reply = response.get("reply", "")
                #         if reply:
                #             conversation.append({"sender": "chatgpt", "message": reply, "source": "chatgpt"})

                # chatgpt_response = ask_chatgptAPI(
                #     "OpenAI_Completion",
                #     GenerateResponseRequest(
                #         baseStatement=reference_content,
                #         userStatement=user_message
                #     ).model_dump_json(),
                #     'ResponseGenerator',
                #     model="gpt-4o-mini"
                # )

                # generateResponse = GenerateResponseResponse(  **chatgpt_response )
                # if ( generateResponse.responseRelevanceScore > 0.8):
                #     conversation.append({"sender": "chatgpt", "message": generateResponse.responseStatement, "source": "chatgpt"})
                # if ( reference_content != ""):
                #     chatgpt_response = ask_chatgptAPI(
                #         "OpenAI_Completion",
                #         AnalyzeResponseRequest(
                #             baseStatement=reference_content,
                #             userResponse=user_message
                #         ).model_dump_json(),
                #         'ResponseAnalysis',
                #         model="o1-mini"
                #     )

                #     analyzeResponse = AnalyzeResponseResponse(  **chatgpt_response )
                #     for paragraphAnalysisItem in analyzeResponse.paragraphAnalysis:
                #         if ( paragraphAnalysisItem.relevanceScore >= 0.7 ) :
                #             conversation.append({"sender": "chatgpt", "message": paragraphAnalysisItem.paragraphResponse, "source": "chatgpt"})
                edu_step_view(request)
                session = TeachingSession.objects.get(user_id=request.session.session_key)                             


        except json.JSONDecodeError as e:
            # 捕捉 JSON 解碼錯誤
            error_message = f"請再發送一次!"
            conversation.append({
                "sender": "chatgpt", 
                "message": error_message, 
                "source": "chatgpt"
            })
        except Exception as e:
            # 捕捉其他一般錯誤
            error_message = f"請再發送一次!"
            #error_message = f"發生未預期的錯誤：{str(e)}"
            conversation.append({
                "sender": "chatgpt", 
                "message": error_message, 
                "source": "error"
            })
        request.session['conversation'] = conversation
        session.save()
        return render(request, 'blog/chat_body.html', {'conversation': conversation})

def init_teaching_session(request):
    request.session.flush()  # 清除對話數據

    # 初始化會話
    user_id = request.session.session_key    
    if not user_id:
        request.session.create()
        user_id = request.session.session_key

    # 重置 TeachingSession
    session, created = TeachingSession.objects.get_or_create(user_id=user_id)
    session.current_step = 0  # 設置初始步驟
    session.guide_key = 0  # 新增 Guide 索引
    session.question_displayed = False  # Question 是否已顯示
    session.current_state = "Idle"  # 初始化狀態
    session.save()

    # 初始化對話內容
    conversation = []


#@login_required
# Chat 主要功能
@custom_login_required
def edu_step_view(request):
    sender = "EduDoc"
    source = "step"

    if request.method == 'GET':
        conversation = []
        session = TeachingSession.objects.get(user_id=request.session.session_key)
        conversation.append({"sender": "chatgpt", "message": session.last_user_situation, "source": "chatgpt"})

    if request.method == 'POST':
        conversation = request.session.get('conversation', [])
        user_message = request.POST.get('message', '').strip()
        session = TeachingSession.objects.get(user_id=request.session.session_key)

    # 處理當前步驟
    if session.current_step < len(step_queue):
        step_data = step_queue[session.current_step]  # 獲取當前步驟
        statement = step_data.get("statement", "")
        content = step_data.get("content", {})

        # 判斷是否需要顯示 Question
        if not session.question_displayed and "Question" in content:
            session.current_state = "Question"
            question = content["Question"]
            question_description = question.get('Description', '').strip()
            question_images = question.get('Images', [])

            # 構造 Question 訊息
            question_message = f"{statement}\n\n<b>[Question]</b>: {question_description}"
            if question_images:
                for image in question_images:
                    question_message += f"\n{image}"  # 使用 Markdown 格式嵌入圖片

            next_step = msg_to_viewMsg(sender, question_message, source)
            conversation.append(next_step)
            session.question_displayed = True
            session.guide_key = "Guide1"
        else:
            # 顯示 Guides 中的 Description
            guides = content.get("Guides", [])
            if session.guide_key in guides:
                session.current_state = "Guide"
                guide = guides[session.guide_key]
                guide_message = f"<b>[Question]</b>: {guide.get('Description', '').strip()}"
                guide_images = guides[session.guide_key].get('Images',[])
                if guide_images:
                    for image in guide_images:
                        guide_message += f"\n{image}"  # 使用 Markdown 格式嵌入圖片                
                next_step = msg_to_viewMsg(sender, guide_message, source)
                conversation.append(next_step)
            elif content.get("Debug", False):
                session.current_state = "Debug"
                # 顯示 Debug 的內容
                debug_message = content.get("Debug", {}).get("Description", "無其他內容。")
                next_step = msg_to_viewMsg(sender, debug_message.strip(), source)
                conversation.append(next_step)
                session.current_step += 1
                session.guide_key = 0
                session.question_displayed = False
            else:
                session.current_state = "Idle"                
                session.current_step += 1
                session.guide_key = "Guide1"
                session.question_displayed = False
                if ( statement != ""):
                    next_step = msg_to_viewMsg(sender, statement, source)
                    conversation.append(next_step)


        session.save()
    else:
        next_step = msg_to_viewMsg(sender, '完成課程囉~ ^_^', source)

    # 儲存對話
    request.session['conversation'] = conversation

    if request.method == 'GET':
        return render(request, 'blog/chat_window.html', {'conversation': conversation})
    elif request.method == 'POST':
        return render(request, 'blog/chat_body.html', {'conversation': [next_step]})

def msg_to_viewMsg(sender:str, msg:str, source:str):
    viewURLs = urlProcessor.extract_specific_urls(msg, [ 'youtube','drive.google.com/file' ])
    if viewURLs:
        msg = utility.replace_specific_string_in_StringlistContent_with_custom_text(msg, viewURLs, replacement='')
        msg = utility.clean_up_text(msg)
        embeddedURLs = urlProcessor.convert_viewURLs_to_embeddedURLs( viewURLs )
        return {"sender": sender, "message": msg, "source": source, "videoURL":embeddedURLs}
    return {"sender": sender, "message": msg, "source": source}

def increment_guide_number(guide_str):
    """
    Increments the last number in a guide string.
    Examples:
    - "Guide1" -> "Guide2"
    - "Guide1.1" -> "Guide1.2"
    - "Guide1.1.1" -> "Guide1.1.2"
    
    Args:
        guide_str (str): The guide string to increment
        
    Returns:
        str: The incremented guide string
    """
    # Split the string into prefix and numbers
    prefix = 'Guide'
    numbers = guide_str[len(prefix):].split('.')
    
    # Increment the last number
    if numbers:
        numbers[-1] = str(int(numbers[-1]) + 1)
    
    # Reconstruct the string
    return prefix + '.'.join(numbers)

def get_next_guide_number(guide_str, guide_dict, isCorrect:bool):
    """
    根據輸入的guide字串和字典，回傳下一個可用的guide號碼
    
    Args:
        guide_str (str): 輸入的guide字串，例如 "Guide1.1" 或 "Guide1.1.1"
        guide_dict (dict): 包含現有guide號碼的字典
        
    Returns:
        str: 下一個可用的guide號碼
    """
    
    if ( isCorrect==False ):
        next_guide = guide_str+".1"
        if next_guide in guide_dict:
            return next_guide

    next_guide = guide_str
    
    # 如果不存在，檢查是否包含點號
    if ( '.' in next_guide):
        while '.' in next_guide:
            next_guide = increment_guide_number(next_guide)
        
            # 如果下一個序號存在於字典中，直接回傳
            if next_guide in guide_dict:
                return next_guide
            # 取得最後一層數字並+1
            prefix = 'Guide'
            numbers = next_guide[len(prefix):].split('.')
            numbers = numbers[:-1]  # 取得除了最後一個數字外的所有數字
            numbers[-1] = str(int(numbers[-1]))
            next_guide = "Guide" + '.'.join(numbers)
        # 無點號，直接使用increment_guide_number的結果

    next_guide = increment_guide_number(next_guide)
    if next_guide in guide_dict:
        return next_guide        
    return "-1"
