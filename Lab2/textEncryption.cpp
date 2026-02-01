#include "textEncryption.h"
#include <iostream>

void EncryptableText::shiftLetter(QChar& letter, int shift)
{
    for (auto &alphabet : alphabets)
    {
        if (alphabet.contains(letter, Qt::CaseInsensitive))
        {
            bool isUpper = letter.isUpper();
            int index = alphabet.indexOf(letter, Qt::CaseInsensitive) + shift;
            index %= alphabet.size();
            if (index < 0)
            {
                index += alphabet.size();
            }

            letter = isUpper ? alphabet[index+1].toUpper() : alphabet[index];
            return;
        }
    }
}

QString& EncryptableText::EncryptCeasar(int shift, const QString& text)
{
    cryptedText = text;

    for (auto &c : cryptedText)
    {
        if (c.isLetter())
        {
            shiftLetter(c, shift);
        }
    }

    return cryptedText;
}

QString& EncryptableText::DecryptCeasar(int shift, const QString& cryptedText)
{
    text = cryptedText;
    
    for (auto &c : text)
    {
        if (c.isLetter())
        {
            shiftLetter(c, -shift);
        }
    }

    return text;
}

QString& EncryptableText::EncryptVegener(const QString& keyword, const QString& text)
{
    cryptedText = text;
    QQueue<int> shifts;

    for (auto &c: keyword.toLower())
    {
        for (auto &alphabet : alphabets)
        {
            if (alphabet.contains(c, Qt::CaseInsensitive))
            {
                shifts.append(alphabet.indexOf(c, Qt::CaseInsensitive) + 1);
                break;
            }
        }
    }
    
    for (auto &c : cryptedText)
    {
        if (c.isLetter())
        {
            shiftLetter(c, shifts.first());
            shifts.enqueue(shifts.dequeue());
        }
    }

    return cryptedText;
}

QString& EncryptableText::DecryptVegener(const QString& keyword, const QString& cryptedText)
{
    text = cryptedText;
    QQueue<int> shifts;

    for (auto &c: keyword.toLower())
    {
        for (auto &alphabet : alphabets)
        {
            if (alphabet.contains(c, Qt::CaseInsensitive))
            {
                shifts.append(alphabet.indexOf(c, Qt::CaseInsensitive) + 1);
                break;
            }
        }
    }
    
    for (auto &c : text)
    {
        if (c.isLetter())
        {
            shiftLetter(c, -shifts.first());
            shifts.enqueue(shifts.dequeue());
        }
    }

    return text;
}