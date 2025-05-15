import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)
import joblib
import pandas as pd

# Загрузка модели
model = joblib.load(r'D:\artem\code\python\telegram_bot\churn_model.pkl')

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определение состояний
CREDIT_SCORE, AGE, TENURE, BALANCE, NUM_PRODUCTS, HAS_CR_CARD, IS_ACTIVE, SALARY = range(8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я помогу предсказать, уйдет ли клиент из банка.\n"
        "Пожалуйста, введите кредитный рейтинг клиента (от 300 до 850):"
    )
    return CREDIT_SCORE

async def credit_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        credit_score = int(update.message.text)
        if 300 <= credit_score <= 850:
            context.user_data['credit_score'] = credit_score
            await update.message.reply_text("Введите возраст клиента:")
            return AGE
        else:
            await update.message.reply_text("Пожалуйста, введите число от 300 до 850.")
            return CREDIT_SCORE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return CREDIT_SCORE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        age = int(update.message.text)
        if age > 0:
            context.user_data['age'] = age
            await update.message.reply_text("Введите срок сотрудничества с банком (в годах):")
            return TENURE
        else:
            await update.message.reply_text("Пожалуйста, введите положительное число.")
            return AGE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return AGE

async def tenure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        tenure = int(update.message.text)
        if tenure >= 0:
            context.user_data['tenure'] = tenure
            await update.message.reply_text("Введите баланс на счету клиента:")
            return BALANCE
        else:
            await update.message.reply_text("Пожалуйста, введите неотрицательное число.")
            return TENURE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return TENURE

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        balance = float(update.message.text)
        context.user_data['balance'] = balance
        await update.message.reply_text("Введите количество продуктов банка, которыми пользуется клиент:")
        return NUM_PRODUCTS
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return BALANCE

async def num_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        num_products = int(update.message.text)
        if num_products > 0:
            context.user_data['num_products'] = num_products
            await update.message.reply_text("Есть ли у клиента кредитная карта? (да/нет):")
            return HAS_CR_CARD
        else:
            await update.message.reply_text("Пожалуйста, введите положительное число.")
            return NUM_PRODUCTS
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return NUM_PRODUCTS

async def has_cr_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.lower()
    if text in ['да', 'нет']:
        context.user_data['has_cr_card'] = 1 if text == 'да' else 0
        await update.message.reply_text("Является ли клиент активным пользователем? (да/нет):")
        return IS_ACTIVE
    else:
        await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет'.")
        return HAS_CR_CARD

async def is_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.lower()
    if text in ['да', 'нет']:
        context.user_data['is_active'] = 1 if text == 'да' else 0
        await update.message.reply_text("Введите предполагаемую зарплату клиента:")
        return SALARY
    else:
        await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет'.")
        return IS_ACTIVE

async def salary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        salary = float(update.message.text)
        context.user_data['salary'] = salary
        
        # Собираем все данные
        data = {
            'CreditScore': [context.user_data['credit_score']],
            'Age': [context.user_data['age']],
            'Tenure': [context.user_data['tenure']],
            'Balance': [context.user_data['balance']],
            'NumOfProducts': [context.user_data['num_products']],
            'HasCrCard': [context.user_data['has_cr_card']],
            'IsActiveMember': [context.user_data['is_active']],
            'EstimatedSalary': [context.user_data['salary']]
        }
        
        # Создаем DataFrame
        df = pd.DataFrame(data)
        
        # Делаем предсказание
        prediction = model.predict(df)
        probability = model.predict_proba(df)[0][1]
        
        # Формируем ответ
        result = "вероятно УЙДЕТ" if prediction[0] == 1 else "вероятно ОСТАНЕТСЯ"
        response = (
            f"Результат предсказания: клиент {result} из банка.\n"
            f"Вероятность ухода: {probability*100:.2f}%"
        )
        
        await update.message.reply_text(response)
        
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return SALARY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Диалог прерван. Чтобы начать заново, введите /start')
    return ConversationHandler.END

def main() -> None:
    # Создаем Application с вашим токеном
    application = Application.builder().token("7339005889:AAFxaiUhmjf5pRhzxgOF4p6VF6lBF0GOpng").build()

    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CREDIT_SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, credit_score)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            TENURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, tenure)],
            BALANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, balance)],
            NUM_PRODUCTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, num_products)],
            HAS_CR_CARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, has_cr_card)],
            IS_ACTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, is_active)],
            SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, salary)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
