variable "apim_name" {
  type          = string  
  description   = "api management name"  
}    


variable "resource_group_name" {
  type          = string  
  description   = "api management resource_group_name"
}    

variable "location" {
  type          = string  
  description   = "api management location"  
}    


variable "sku_name" {
  type          = string  
  description   = "api management sku"  
  default       = "Developer_1"
}    

variable "publisher_name" {
  type          = string  
  description   = "api management publisher neam"  
}    

variable "publisher_email" {
  type          = string  
  description   = "api management publisher email"  
}    

variable "virtual_network_type" {
  type          = string  
  description   = "api management virtual network type"  
} 

variable "tags" {
  description   = "api management resource tags"  

  default       = { 
        "Created By" = "Terraform"
    }
}