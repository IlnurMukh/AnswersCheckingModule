using AnswersCheckingModule.Models;

namespace AnswersCheckingModule.Interfaces;

public interface IAnswerRepository
{
    Task<Answer> GetAnswerAsync(int id);
    Task<IEnumerable<Answer>> GetAnswersAsync(Question question);
    Task<bool> AddAnswerAsync(User user, string answerText, Question question);
    Task<bool> SaveAsync();
}