using AnswersCheckingModule.Models;

namespace AnswersCheckingModule.Interfaces;

public interface IAccountRepository
{
    Task<User> GetUserAsync(int id);
    Task<User?> GetUserAsync(string username, string password);

    Task<bool> AddUserAsync(string username, string password);
    Task<bool> SaveAsync();
}