using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text;

namespace AnswersCheckingModule.Models
{
    public class Question
    {
        [Key]
        public int Id { get; set; }

        [Required] 
        public  string UniqueCode { get; } = GetUniqueCode();
        [Required]
        public string Title { get; set; }
        [Required]
        public string CorrectAnswer { get; set; }
        [Required]
        public int OwnerId { get; set; }
        [ForeignKey("OwnerId")]
        public User Owner { get; set; }

        private static string GetUniqueCode()
        {
            var builder = new StringBuilder();
            Enumerable
                .Range(65, 26)
                .Select(e => ((char)e).ToString())
                .Concat(Enumerable.Range(97, 26).Select(e => ((char)e).ToString()))
                .Concat(Enumerable.Range(0, 10).Select(e => e.ToString()))
                .OrderBy(e => Guid.NewGuid())
                .Take(8)
                .ToList().ForEach(e => builder.Append(e));
            return builder.ToString();
        }
    }
}
