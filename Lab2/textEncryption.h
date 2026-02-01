#include <QString>
#include <QList>
#include <QQueue>

class EncryptableText
{
    QString text;
    QString cryptedText;

    void shiftLetter(QChar& letter, int shift);

public:
    const QList<QString> alphabets = {
        "abcdefghijklmnopqrstuvwxyz",
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    };

    QString& EncryptCeasar(int shift, const QString& text);
    QString& DecryptCeasar(int shift, const QString& cryptedText);

    QString& EncryptVegener(const QString& keyword, const QString& text);
    QString& DecryptVegener(const QString& keyword, const QString& cryptedText);
};