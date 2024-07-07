using AnswersCheckingModule.Interfaces;
using AnswersCheckingModule.Models;
using Microsoft.EntityFrameworkCore;

namespace AnswersCheckingModule.Repositories;

public class AnswerRepository : IAnswerRepository
{
    private readonly AppDbContext _appDbContext;

    public AnswerRepository(AppDbContext context)
    {
        _appDbContext = context;
    }
    public Task<Answer> GetAnswerAsync(int id)
    {
        return _appDbContext.Answers.FirstAsync(a => a.Id == id);
    }

    public async Task<IEnumerable<Answer>> GetAnswersAsync(Question question)
    {
        return _appDbContext.Answers.Where(a => a.Question == question);
    }

    public async Task<bool> AddAnswerAsync(User user, string answerText, Question question)
    {
        await _appDbContext.Answers.AddAsync(new Answer() 
                { AnswerText = answerText, Question = question, User = user })
            .ConfigureAwait(false);
        return await SaveAsync().ConfigureAwait(false);
    }

    public async Task<bool> SaveAsync()
    {
        return await _appDbContext.SaveChangesAsync().ConfigureAwait(false) > 0;
    }
}