import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Указываем полный путь к файлу
file_path = r'D:\artem\code\python\telegram_bot\Churn_Modelling.csv'

try:
    # Загрузка датасета
    data = pd.read_csv(file_path)
    print("Файл успешно загружен!")
    print(f"Количество записей: {len(data)}")
    
    # Выведем первые 5 строк для проверки
    print("\nПервые 5 строк данных:")
    print(data.head())
    
    # Предполагаем, что столбец с целевой переменной называется 'Exited'
    # Если у вас другое название - измените
    target_column = 'Exited'
    
    # Выбираем фичи для модели (адаптируйте под ваш датасет)
    features = ['CreditScore', 'Age', 'Tenure', 'Balance', 
                'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary']
    
    # Проверяем, что все фичи существуют в датасете
    missing_features = [f for f in features if f not in data.columns]
    if missing_features:
        raise ValueError(f"Отсутствуют колонки: {missing_features}")
    
    if target_column not in data.columns:
        raise ValueError(f"Отсутствует целевая колонка: {target_column}")
    
    # Разделение на обучающую и тестовую выборки
    X = data[features]
    y = data[target_column]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Обучение модели
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Проверка точности
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy модели: {accuracy:.2f}")
    
    # Сохранение модели
    model_path = r'D:\artem\code\python\telegram_bot\churn_model.pkl'
    joblib.dump(model, model_path)
    print(f"Модель сохранена по пути: {model_path}")

except FileNotFoundError:
    print(f"Ошибка: Файл не найден по пути {file_path}")
    print("Проверьте:")
    print("1. Правильность пути")
    print("2. Что файл существует")
    print("3. Что имя файла указано верно (учтите регистр букв)")
except Exception as e:
    print(f"Произошла ошибка: {str(e)}")
