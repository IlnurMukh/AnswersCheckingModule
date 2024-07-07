using AnswersCheckingModule.Models;

namespace AnswersCheckingModule.Interfaces;

public interface IQuestionRepository
{
    Task<Question?> GetQuestionAsync(string uniqueCode);
    Task<IEnumerable<Question>> GetQuestionsAsync(User owner);
    Task<bool> AddQuestionAsync(string title, string correctAnswer, User owner);
    Task<bool> SaveAsync();
}