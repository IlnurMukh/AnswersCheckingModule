using AnswersCheckingModule.Interfaces;
using AnswersCheckingModule.Models;
using Microsoft.EntityFrameworkCore;

namespace AnswersCheckingModule.Repositories;

public class AccountRepository : IAccountRepository
{
    private readonly AppDbContext _appDbContext;

    public AccountRepository(AppDbContext context)
    {
        _appDbContext = context;
    }
    public Task<User> GetUserAsync(int id)
    {
        return _appDbContext.Users.FirstAsync(u => u.Id == id);
    }

    public Task<User?> GetUserAsync(string username, string password)
    {
        return _appDbContext.Users.FirstOrDefaultAsync(u => u.Username == username && u.Password == password);
    }

    public async Task<bool> AddUserAsync(string username, string password)
    {
        var user = await _appDbContext.Users.FirstOrDefaultAsync(u => u.Username == username).ConfigureAwait(false);
        if (user != null)
            return false;
        user = new User() { Username = username, Password = password };
        await _appDbContext.Users.AddAsync(user).ConfigureAwait(false);
        return await SaveAsync().ConfigureAwait(false);
    }

    public async Task<bool> SaveAsync()
    {
        return await _appDbContext.SaveChangesAsync().ConfigureAwait(false) > 0;
    }
}