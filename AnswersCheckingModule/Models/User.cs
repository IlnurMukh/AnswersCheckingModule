﻿using System.ComponentModel.DataAnnotations;

namespace AnswersCheckingModule.Models
{
    public class User
    {
        [Key]
        public int Id { get; set; }
        [Required]
        public string Username { get; set; }
        [Required]
        public string Password { get; set; }
    }
}
