using AnswersCheckingModule.Interfaces;
using AnswersCheckingModule.Models;
using Microsoft.EntityFrameworkCore;

namespace AnswersCheckingModule.Repositories;

public class QuestionRepository : IQuestionRepository
{
    private readonly AppDbContext _appDbContext;

    public QuestionRepository(AppDbContext context)
    {
        _appDbContext = context;
    }
    public Task<Question?> GetQuestionAsync(string uniqueCode)
    {
        return _appDbContext.Questions.FirstOrDefaultAsync(q => q.UniqueCode == uniqueCode);
    }

    public async Task<IEnumerable<Question>> GetQuestionsAsync(User owner)
    {
        return _appDbContext.Questions.Where(q => q.Owner == owner);
    }

    public async Task<bool> AddQuestionAsync(string title, string correctAnswer, User owner)
    {
        await _appDbContext.Questions.AddAsync(new Question()
            { Title = title, CorrectAnswer = correctAnswer, Owner = owner }).ConfigureAwait(false);
        return await SaveAsync().ConfigureAwait(false);
    }

    public async Task<bool> SaveAsync()
    {
        return await _appDbContext.SaveChangesAsync().ConfigureAwait(false) > 0;
    }
}